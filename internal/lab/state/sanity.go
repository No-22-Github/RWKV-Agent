// Package state ports the RWKV time-state tools: the magnitude gate, the
// state evaluation driver and the corpus continuation probe.
package state

import (
	"archive/zip"
	"encoding/binary"
	"fmt"
	"io"
	"math"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
)

// Magnitude gate for uploaded RWKV time-states (g1k 7B layout:
// blocks.N.att.time_state).
//
// A state tuned into a workable regime keeps a small per-tensor RMS; a run
// whose learning rate or step scale is off blows the state up and the model
// degrades even though the training loss may fall. The tensors are read
// straight out of the torch archive — no torch, no model load.

// ReferenceNote is the calibration note the original prints as the epilog.
const ReferenceNote = `Calibration on g1k 7B bf16 time-states (2026-09-20/21, per-tensor median RMS / max|v|):

  RMS 0.0011 / 0.003   ws700 corpus, lr 1e-5   coherent; canary readable; 1/40 workbank
  RMS 0.84   / 3.6     37-row run step 18      degenerate: no tool call at all, canary loops
  RMS 1.06   / 10.3    37-row run step 108     partially coherent; canary garbled; 0/40
  RMS 3.7    / 31      same run, earlier sweep collapsed: word salad, 0/40, no tool variety

Three tiers: ok at or below 0.05 (the band the one coherent state occupied), WARN up to
2.0 (degraded but not collapsed: probe before spending eval budget), FAIL above 2.0 or on
any NaN/Inf. The gate is a warning, not a verdict — a canary request costs seconds and
settles what the numbers only flag.`

// tensorStats is one tensor's magnitude summary.
type tensorStats struct {
	Name     string
	RMS      float64
	MaxAbs   float64
	NaN      int
	Inf      int
	Elements int
}

// stateStats is one state file's summary.
type stateStats struct {
	Path      string
	Dtype     string
	Tensors   []tensorStats
	MedianRMS float64
	MaxAbs    float64
	NaN       int
	Inf       int
}

func dtypeOf(archive *zip.ReadCloser) (string, error) {
	var raw []byte
	for _, file := range archive.File {
		if file.Name == "archive/data.pkl" {
			reader, err := file.Open()
			if err != nil {
				return "", err
			}
			raw, err = io.ReadAll(reader)
			reader.Close()
			if err != nil {
				return "", err
			}
			break
		}
	}
	text := string(raw)
	switch {
	case strings.Contains(text, "BFloat16Storage"):
		return "bf16", nil
	case strings.Contains(text, "HalfStorage"):
		return "fp16", nil
	case strings.Contains(text, "FloatStorage"):
		return "fp32", nil
	}
	return "", fmt.Errorf("%s: unrecognised storage dtype", archiveName(archive))
}

func archiveName(archive *zip.ReadCloser) string {
	if len(archive.File) > 0 {
		return archive.File[0].Name
	}
	return ""
}

// decode turns raw storage bytes into float64 values, counting NaN and Inf the
// way the original does. The bf16 path deliberately mirrors its arithmetic:
// subnormals collapse to 0.0 and NaN/Inf contribute 0.0 to the moments.
func decode(raw []byte, dtype string) ([]float64, int, int) {
	switch dtype {
	case "bf16":
		values := make([]float64, 0, len(raw)/2)
		nan, inf := 0, 0
		for i := 0; i+1 < len(raw); i += 2 {
			code := uint16(raw[i]) | uint16(raw[i+1])<<8
			exponent := (code >> 7) & 0xFF
			mantissa := code & 0x7F
			if exponent == 0xFF {
				if mantissa != 0 {
					nan++
				} else {
					inf++
				}
				values = append(values, 0.0)
				continue
			}
			sign := 1.0
			if code>>15 != 0 {
				sign = -1.0
			}
			if exponent == 0 {
				values = append(values, 0.0)
			} else {
				values = append(values, sign*math.Ldexp(float64(mantissa)/128.0+1.0, int(exponent)-127))
			}
		}
		return values, nan, inf
	case "fp32":
		values := make([]float64, 0, len(raw)/4)
		nan, inf := 0, 0
		for i := 0; i+4 <= len(raw); i += 4 {
			v := float64(math.Float32frombits(binary.LittleEndian.Uint32(raw[i:])))
			if v != v {
				nan++
				values = append(values, 0.0)
				continue
			}
			if math.IsInf(v, 0) {
				inf++
				values = append(values, 0.0)
				continue
			}
			values = append(values, v)
		}
		return values, nan, inf
	default: // fp16
		values := make([]float64, 0, len(raw)/2)
		nan, inf := 0, 0
		for i := 0; i+1 < len(raw); i += 2 {
			v := float64(halfToFloat32(binary.LittleEndian.Uint16(raw[i:])))
			if v != v {
				nan++
				values = append(values, 0.0)
				continue
			}
			if math.IsInf(v, 0) {
				inf++
				values = append(values, 0.0)
				continue
			}
			values = append(values, v)
		}
		return values, nan, inf
	}
}

// halfToFloat32 converts an IEEE 754 binary16 to binary32. Exact for every
// finite half including subnormals, so no rounding mode is involved.
func halfToFloat32(h uint16) float32 {
	sign := uint32(h>>15) & 1
	exp := uint32(h>>10) & 0x1F
	mant := uint32(h) & 0x3FF
	var bits uint32
	switch {
	case exp == 0:
		if mant == 0 {
			bits = sign << 31
			break
		}
		e := uint32(127 - 15 + 1)
		for mant&0x400 == 0 {
			mant <<= 1
			e--
		}
		mant &= 0x3FF
		bits = sign<<31 | e<<23 | mant<<13
	case exp == 0x1F:
		bits = sign<<31 | 0xFF<<23 | mant<<13
	default:
		bits = sign<<31 | (exp-15+127)<<23 | mant<<13
	}
	return math.Float32frombits(bits)
}

// stateStatsOf reads one state file.
func stateStatsOf(path string) (*stateStats, error) {
	archive, err := zip.OpenReader(path)
	if err != nil {
		return nil, err
	}
	defer archive.Close()
	dtype, err := dtypeOf(archive)
	if err != nil {
		return nil, err
	}

	type entry struct {
		name  string
		index int
	}
	var entries []entry
	for _, file := range archive.File {
		if !strings.HasPrefix(file.Name, "archive/data/") {
			continue
		}
		suffix := file.Name[strings.LastIndex(file.Name, "/")+1:]
		index, err := strconv.Atoi(suffix)
		if err != nil {
			continue
		}
		entries = append(entries, entry{file.Name, index})
	}
	sort.SliceStable(entries, func(i, j int) bool { return entries[i].index < entries[j].index })

	report := &stateStats{Path: path, Dtype: dtype}
	for _, item := range entries {
		for _, file := range archive.File {
			if file.Name != item.name {
				continue
			}
			reader, err := file.Open()
			if err != nil {
				return nil, err
			}
			raw, err := io.ReadAll(reader)
			reader.Close()
			if err != nil {
				return nil, err
			}
			values, nan, inf := decode(raw, dtype)
			if len(values) == 0 {
				return nil, fmt.Errorf("%s: tensor %s is empty", path, item.name)
			}
			sumSquares := 0.0
			maxAbs := 0.0
			for _, v := range values {
				sumSquares += v * v
				if abs := math.Abs(v); abs > maxAbs {
					maxAbs = abs
				}
			}
			report.Tensors = append(report.Tensors, tensorStats{
				Name: suffixOf(item.name), RMS: math.Sqrt(sumSquares / float64(len(values))),
				MaxAbs: maxAbs, NaN: nan, Inf: inf, Elements: len(values),
			})
			break
		}
	}
	if len(report.Tensors) == 0 {
		return nil, fmt.Errorf("%s: no tensors found", path)
	}
	rmsValues := make([]float64, 0, len(report.Tensors))
	for _, t := range report.Tensors {
		rmsValues = append(rmsValues, t.RMS)
		report.NaN += t.NaN
		report.Inf += t.Inf
		if t.MaxAbs > report.MaxAbs {
			report.MaxAbs = t.MaxAbs
		}
	}
	sort.Float64s(rmsValues)
	report.MedianRMS = rmsValues[len(rmsValues)/2]
	return report, nil
}

func suffixOf(name string) string {
	return name[strings.LastIndex(name, "/")+1:]
}

// SanityArgs are the `state sanity` flags.
type SanityArgs struct {
	States    []string
	Reference string
	WarnRMS   float64
	MaxRMS    float64
	MaxRatio  float64
	HasRatio  bool
	Verbose   bool
}

// RunSanity is the `state sanity` command. Exit code is 1 when a gated state
// fails, so a training loop can stop before spending eval budget.
func RunSanity(args SanityArgs) int {
	var reference *stateStats
	if args.Reference != "" {
		var err error
		reference, err = stateStatsOf(args.Reference)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			return 2
		}
		fmt.Printf("reference %s: dtype=%s median RMS %.6f max|v| %.4f\n",
			filepath.Base(reference.Path), reference.Dtype, reference.MedianRMS, reference.MaxAbs)
	}

	failed := false
	for _, path := range args.States {
		report, err := stateStatsOf(path)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			return 2
		}
		ratio := 0.0
		hasRatio := false
		if reference != nil && reference.MedianRMS != 0 {
			ratio = report.MedianRMS / reference.MedianRMS
			hasRatio = true
		}
		verdict := ""
		switch {
		case report.NaN > 0 || report.Inf > 0:
			verdict = "FAIL (nan/inf present)"
			failed = true
		case report.MedianRMS > args.MaxRMS:
			verdict = fmt.Sprintf("FAIL (median RMS %.3f > ceiling %v)", report.MedianRMS, pyFloat(args.MaxRMS))
			failed = true
		case hasRatio && args.HasRatio && ratio > args.MaxRatio:
			verdict = fmt.Sprintf("FAIL (median RMS %.0fx reference)", ratio)
			failed = true
		case report.MedianRMS > args.WarnRMS:
			verdict = fmt.Sprintf("WARN (median RMS %.3f above coherent band; probe behaviour first)", report.MedianRMS)
		}
		line := fmt.Sprintf("%s: dtype=%s tensors=%d median RMS %.6f max|v| %.4f nan=%d inf=%d",
			filepath.Base(path), report.Dtype, len(report.Tensors), report.MedianRMS,
			report.MaxAbs, report.NaN, report.Inf)
		if hasRatio && ratio != 0 {
			line += fmt.Sprintf(" ratio=%.0fx", ratio)
		}
		if verdict != "" {
			line += " -> " + verdict
		} else {
			line += " -> ok"
		}
		fmt.Println(line)
		if args.Verbose {
			for _, tensor := range report.Tensors {
				fmt.Printf("    %4s rms %.6f max|v| %.4f\n", tensor.Name, tensor.RMS, tensor.MaxAbs)
			}
		}
	}
	if failed {
		return 1
	}
	return 0
}

// pyFloat is Python's str() for the float that goes into the FAIL message.
func pyFloat(f float64) string {
	s := strconv.FormatFloat(f, 'g', -1, 64)
	if !strings.ContainsAny(s, ".eE") {
		s += ".0"
	}
	return s
}
