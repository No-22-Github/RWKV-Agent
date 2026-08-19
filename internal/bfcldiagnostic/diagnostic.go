package bfcldiagnostic

import (
	"bufio"
	"encoding/json"
	"fmt"
	"math"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/bfcl"
)

type SplitResult struct {
	Category         string
	FullCorrect      int
	FullTotal        int
	SampleCorrect    int
	SampleTotal      int
	DeltaPP          float64
	ThresholdPP      float64
	TriggerExpansion bool
}

type Report struct {
	ManifestPath   string
	ManifestSHA256 string
	ScoreRoot      string
	ModelName      string
	Splits         []SplitResult
}

type scoreSummary struct {
	Accuracy     float64 `json:"accuracy"`
	CorrectCount int     `json:"correct_count"`
	TotalCount   int     `json:"total_count"`
}

type scoreEntry struct {
	ID    string `json:"id"`
	Valid bool   `json:"valid"`
}

func Analyze(manifestPath, scoreRoot string) (Report, error) {
	manifest, digest, err := bfcl.LoadSampleManifest(manifestPath)
	if err != nil {
		return Report{}, err
	}
	report := Report{
		ManifestPath:   filepath.Clean(manifestPath),
		ManifestSHA256: digest,
		ScoreRoot:      filepath.Clean(scoreRoot),
		Splits:         make([]SplitResult, 0, len(manifest.Splits)),
	}
	for _, split := range manifest.Splits {
		path, modelName, err := findScoreFile(scoreRoot, split.Category)
		if err != nil {
			return Report{}, err
		}
		if report.ModelName == "" {
			report.ModelName = modelName
		} else if report.ModelName != modelName {
			return Report{}, fmt.Errorf("BFCL score root mixes models %q and %q", report.ModelName, modelName)
		}
		summary, failed, err := readScore(path)
		if err != nil {
			return Report{}, err
		}
		if summary.TotalCount != split.Population || summary.CorrectCount+len(failed) != summary.TotalCount {
			return Report{}, fmt.Errorf(
				"BFCL score %s is not a complete %s run: correct=%d failed=%d total=%d population=%d",
				path,
				split.Category,
				summary.CorrectCount,
				len(failed),
				summary.TotalCount,
				split.Population,
			)
		}
		expectedAccuracy := float64(summary.CorrectCount) / float64(summary.TotalCount)
		if math.Abs(summary.Accuracy-expectedAccuracy) > 1e-12 {
			return Report{}, fmt.Errorf("BFCL score %s has inconsistent accuracy", path)
		}
		sampleFailed := 0
		for _, id := range split.IDs {
			if failed[id] {
				sampleFailed++
			}
		}
		sampleCorrect := split.SampleSize - sampleFailed
		fullAccuracy := 100 * float64(summary.CorrectCount) / float64(summary.TotalCount)
		sampleAccuracy := 100 * float64(sampleCorrect) / float64(split.SampleSize)
		delta := sampleAccuracy - fullAccuracy
		threshold := 200 / float64(split.SampleSize)
		report.Splits = append(report.Splits, SplitResult{
			Category:         split.Category,
			FullCorrect:      summary.CorrectCount,
			FullTotal:        summary.TotalCount,
			SampleCorrect:    sampleCorrect,
			SampleTotal:      split.SampleSize,
			DeltaPP:          delta,
			ThresholdPP:      threshold,
			TriggerExpansion: math.Abs(delta) > threshold,
		})
	}
	return report, nil
}

func TriggeredSplits(report Report) map[string]bool {
	triggered := make(map[string]bool)
	for _, split := range report.Splits {
		if split.TriggerExpansion {
			triggered[split.Category] = true
		}
	}
	return triggered
}

func RenderMarkdown(report Report, v2Path, v2SHA256 string) []byte {
	var output strings.Builder
	output.WriteString("# BFCL v4 M3 抽样代表性诊断\n\n")
	output.WriteString("- 诊断模型：`" + report.ModelName + "`\n")
	output.WriteString("- 冻结清单：`" + report.ManifestPath + "`\n")
	output.WriteString("- v1 SHA-256：`" + report.ManifestSHA256 + "`\n")
	output.WriteString("- 官方 score 根目录：`" + report.ScoreRoot + "`\n")
	output.WriteString("- 口径：同一次 Qwen3-8B 增强档全量运行；按冻结 ID 从官方逐题失败记录反推抽样正确数。\n\n")
	output.WriteString("| Split | 抽样 | 全量 | 偏差 | 机械阈值 | 扩额 |\n")
	output.WriteString("|---|---:|---:|---:|---:|---|\n")
	for _, split := range report.Splits {
		trigger := "否"
		if split.TriggerExpansion {
			trigger = "是"
		}
		fmt.Fprintf(
			&output,
			"| `%s` | %d/%d (%.2f%%) | %d/%d (%.2f%%) | %+.2f pp | %.2f pp | %s |\n",
			split.Category,
			split.SampleCorrect,
			split.SampleTotal,
			100*float64(split.SampleCorrect)/float64(split.SampleTotal),
			split.FullCorrect,
			split.FullTotal,
			100*float64(split.FullCorrect)/float64(split.FullTotal),
			split.DeltaPP,
			split.ThresholdPP,
			trigger,
		)
	}
	output.WriteString("\n")
	if v2Path == "" {
		output.WriteString("没有 split 触发机械扩额；五格矩阵统一使用 manifest v1。\n")
	} else {
		output.WriteString("至少一个 split 触发机械扩额；五格矩阵统一使用 manifest v2。\n\n")
		output.WriteString("- v2 清单：`" + v2Path + "`\n")
		output.WriteString("- v2 SHA-256：`" + v2SHA256 + "`\n")
	}
	output.WriteString("\n## 解释边界\n\n")
	output.WriteString("该抽样集只对 Qwen3-8B 在本次增强档配置下的表现做代表性诊断；不能推出它对所有模型、所有档位普遍具有代表性，尤其不能声称对 RWKV 具有代表性。\n")
	return []byte(output.String())
}

func WriteReport(path string, content []byte) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		return err
	}
	return os.WriteFile(path, content, 0o600)
}

func findScoreFile(root, category string) (string, string, error) {
	name := "BFCL_v4_" + category + "_score.json"
	var matches []string
	err := filepath.WalkDir(root, func(path string, entry os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if !entry.IsDir() && entry.Name() == name {
			matches = append(matches, path)
		}
		return nil
	})
	if err != nil {
		return "", "", err
	}
	if len(matches) != 1 {
		return "", "", fmt.Errorf("expected one %s under %s, found %d", name, root, len(matches))
	}
	sort.Strings(matches)
	relative, err := filepath.Rel(root, matches[0])
	if err != nil {
		return "", "", err
	}
	parts := strings.Split(relative, string(filepath.Separator))
	if len(parts) < 3 {
		return "", "", fmt.Errorf("cannot derive model name from BFCL score path %s", matches[0])
	}
	return matches[0], parts[0], nil
}

func readScore(path string) (scoreSummary, map[string]bool, error) {
	file, err := os.Open(path)
	if err != nil {
		return scoreSummary{}, nil, err
	}
	defer file.Close()
	scanner := bufio.NewScanner(file)
	scanner.Buffer(make([]byte, 64*1024), 16*1024*1024)
	if !scanner.Scan() {
		return scoreSummary{}, nil, fmt.Errorf("BFCL score %s is empty", path)
	}
	var summary scoreSummary
	if err := json.Unmarshal(scanner.Bytes(), &summary); err != nil {
		return scoreSummary{}, nil, fmt.Errorf("decode BFCL score summary %s: %w", path, err)
	}
	failed := make(map[string]bool)
	for scanner.Scan() {
		var entry scoreEntry
		if err := json.Unmarshal(scanner.Bytes(), &entry); err != nil {
			return scoreSummary{}, nil, fmt.Errorf("decode BFCL score entry %s: %w", path, err)
		}
		if entry.ID == "" || entry.Valid {
			return scoreSummary{}, nil, fmt.Errorf("unexpected BFCL score detail in %s", path)
		}
		if failed[entry.ID] {
			return scoreSummary{}, nil, fmt.Errorf("duplicate BFCL score id %q", entry.ID)
		}
		failed[entry.ID] = true
	}
	if err := scanner.Err(); err != nil {
		return scoreSummary{}, nil, err
	}
	return summary, failed, nil
}
