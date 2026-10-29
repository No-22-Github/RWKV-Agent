package eval

import (
	"bufio"
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"time"
)

// CheckpointSchemaVersion versions the <output>.partial layout.
const CheckpointSchemaVersion = 1

const (
	checkpointSignatureFile = "signature.json"
	checkpointCasesFile     = "cases.jsonl"
	checkpointProgressFile  = "progress.json"
)

// Case statuses as printed on the progress line and stored per checkpoint.
const (
	CaseStatusPass    = "pass"
	CaseStatusFail    = "fail"
	CaseStatusInvalid = "invalid"
)

// CaseCheckpoint is one finished case, one line of cases.jsonl. Result and
// Trace are exactly what the final summary.json and trace.jsonl carry for the
// case (trace sequence numbers are reassigned when the run is merged).
type CaseCheckpoint struct {
	Index      int           `json:"index"`
	CaseID     string        `json:"case_id"`
	Status     string        `json:"status"`
	ElapsedMS  int64         `json:"elapsed_ms"`
	FinishedAt time.Time     `json:"finished_at"`
	Result     CaseResult    `json:"result"`
	Trace      []TraceRecord `json:"trace"`
}

// CheckpointProgress is progress.json: a snapshot rewritten after every case.
type CheckpointProgress struct {
	SchemaVersion int    `json:"schema_version"`
	RunID         string `json:"run_id"`
	Total         int    `json:"total"`
	Done          int    `json:"done"`
	Pass          int    `json:"pass"`
	Fail          int    `json:"fail"`
	Invalid       int    `json:"invalid"`
	// Resumed counts the cases carried over from earlier attempts (part of
	// Done); they are not run again.
	Resumed          int       `json:"resumed"`
	StartedAt        time.Time `json:"started_at"`
	AttemptStartedAt time.Time `json:"attempt_started_at"`
	UpdatedAt        time.Time `json:"updated_at"`
	// ETASeconds and ETAAt estimate when the remaining cases finish, from this
	// attempt's throughput (see estimateETA); absent until enough cases of
	// this attempt have finished.
	ETASeconds *int64     `json:"eta_seconds,omitempty"`
	ETAAt      *time.Time `json:"eta_at,omitempty"`
}

// checkpointHeader is signature.json: the run identity and the configuration
// signature a resume must match.
type checkpointHeader struct {
	SchemaVersion int               `json:"schema_version"`
	RunID         string            `json:"run_id"`
	StartedAt     time.Time         `json:"started_at"`
	Signature     map[string]string `json:"signature"`
}

// Checkpoint persists an eval run case by case under <output>.partial so an
// interrupted run keeps its finished cases and can be resumed. All methods
// are safe on a nil receiver, which disables checkpointing.
type Checkpoint struct {
	dir       string
	runID     string
	startedAt time.Time
	log       io.Writer
	now       func() time.Time

	// done holds the cases earlier attempts finished with a usable result;
	// invalid and infrastructure-broken ones (NeedsRerun) are left out so
	// they run again.
	done map[string]CaseCheckpoint

	mu       sync.Mutex
	file     *os.File
	progress CheckpointProgress
	warned   bool
}

// PartialDir is the checkpoint directory that belongs to an eval output.
func PartialDir(output string) string {
	return filepath.Clean(output) + ".partial"
}

// OpenCheckpoint creates the checkpoint for output, or with resume reopens an
// existing one after checking that config produces the same signature. An
// existing checkpoint without resume is an error, so a stale partial is
// never silently mixed into or overwritten by a new run. Progress lines go to
// log (nil discards them).
func OpenCheckpoint(output string, config Config, resume bool, log io.Writer) (*Checkpoint, error) {
	if output == "" {
		return nil, fmt.Errorf("eval output directory is required")
	}
	absolute, err := filepath.Abs(output)
	if err != nil {
		return nil, err
	}
	config, err = normalizeConfig(config)
	if err != nil {
		return nil, err
	}
	if log == nil {
		log = io.Discard
	}
	now := config.Now
	if now == nil {
		now = time.Now
	}
	signature := RunSignature(runManifest(config, "", time.Time{}))
	checkpoint := &Checkpoint{
		dir:  PartialDir(absolute),
		log:  log,
		now:  now,
		done: map[string]CaseCheckpoint{},
	}
	if _, err := os.Stat(checkpoint.dir); err == nil {
		if !resume {
			return nil, fmt.Errorf(
				"partial results of an interrupted run exist at %s: pass --resume to continue it, "+
					"or remove the directory to start over", checkpoint.dir)
		}
		if err := checkpoint.reopen(config, signature); err != nil {
			return nil, err
		}
		return checkpoint, nil
	} else if !errors.Is(err, os.ErrNotExist) {
		return nil, err
	}
	if err := checkpoint.create(config, signature); err != nil {
		return nil, err
	}
	return checkpoint, nil
}

func (c *Checkpoint) create(config Config, signature map[string]string) error {
	started := c.now().UTC()
	c.runID = started.Format("20060102T150405.000000000Z")
	c.startedAt = started
	if err := os.MkdirAll(filepath.Dir(c.dir), 0o700); err != nil {
		return err
	}
	if err := os.Mkdir(c.dir, 0o700); err != nil {
		return err
	}
	header := checkpointHeader{
		SchemaVersion: CheckpointSchemaVersion,
		RunID:         c.runID,
		StartedAt:     started,
		Signature:     signature,
	}
	if err := writeJSON(filepath.Join(c.dir, checkpointSignatureFile), header); err != nil {
		return err
	}
	file, err := os.OpenFile(filepath.Join(c.dir, checkpointCasesFile), os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o600)
	if err != nil {
		return err
	}
	c.file = file
	c.progress = CheckpointProgress{
		SchemaVersion:    CheckpointSchemaVersion,
		RunID:            c.runID,
		Total:            len(config.Cases),
		StartedAt:        started,
		AttemptStartedAt: started,
		UpdatedAt:        started,
	}
	return c.writeProgress()
}

func (c *Checkpoint) reopen(config Config, signature map[string]string) error {
	data, err := os.ReadFile(filepath.Join(c.dir, checkpointSignatureFile))
	if err != nil {
		return fmt.Errorf("read checkpoint signature: %w", err)
	}
	var header checkpointHeader
	if err := json.Unmarshal(data, &header); err != nil {
		return fmt.Errorf("decode checkpoint signature %s: %w", c.dir, err)
	}
	if header.SchemaVersion != CheckpointSchemaVersion {
		return fmt.Errorf("resume refused: checkpoint %s has schema_version %d, this binary writes %d",
			c.dir, header.SchemaVersion, CheckpointSchemaVersion)
	}
	if diffs := SignatureDiff(header.Signature, signature); len(diffs) > 0 {
		return fmt.Errorf("resume refused: run configuration differs from checkpoint %s:\n  %s",
			c.dir, strings.Join(diffs, "\n  "))
	}
	c.runID = header.RunID
	c.startedAt = header.StartedAt
	records, validSize, err := readCaseCheckpoints(filepath.Join(c.dir, checkpointCasesFile))
	if err != nil {
		return err
	}
	file, err := os.OpenFile(filepath.Join(c.dir, checkpointCasesFile), os.O_WRONLY, 0o600)
	if err != nil {
		return err
	}
	// A process killed mid-append leaves a torn last line; cut it off so the
	// next record starts on a line of its own.
	if err := file.Truncate(validSize); err != nil {
		_ = file.Close()
		return err
	}
	if _, err := file.Seek(validSize, io.SeekStart); err != nil {
		_ = file.Close()
		return err
	}
	c.file = file
	known := make(map[string]bool, len(config.Cases))
	for _, testCase := range config.Cases {
		known[testCase.ID] = true
	}
	// The last record of a case wins: an invalid case rerun on an earlier
	// resume appends a newer line.
	latest := map[string]CaseCheckpoint{}
	for _, record := range records {
		if known[record.CaseID] {
			latest[record.CaseID] = record
		}
	}
	rerun := 0
	for id, record := range latest {
		if NeedsRerun(record.Result) {
			rerun++
			continue
		}
		c.done[id] = record
	}
	attempt := c.now().UTC()
	c.progress = CheckpointProgress{
		SchemaVersion:    CheckpointSchemaVersion,
		RunID:            c.runID,
		Total:            len(config.Cases),
		Resumed:          len(c.done),
		StartedAt:        c.startedAt,
		AttemptStartedAt: attempt,
		UpdatedAt:        attempt,
	}
	for _, record := range c.done {
		c.progress.Done++
		if record.Status == CaseStatusPass {
			c.progress.Pass++
		} else {
			c.progress.Fail++
		}
	}
	fmt.Fprintf(c.log, "resume: %d/%d cases carried over from %s; %d invalid/infra rerun, %d left to run\n",
		len(c.done), len(config.Cases), c.dir, rerun, len(config.Cases)-len(c.done))
	return c.writeProgress()
}

// readCaseCheckpoints decodes cases.jsonl and returns the byte length of the
// complete lines. Only the final line may be torn; damage before it is an
// error, because a later record would otherwise be lost silently.
func readCaseCheckpoints(path string) ([]CaseCheckpoint, int64, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, 0, fmt.Errorf("read checkpoint cases: %w", err)
	}
	defer file.Close()
	reader := bufio.NewReader(file)
	var records []CaseCheckpoint
	var valid int64
	missingNewline := false
	for line := 1; ; line++ {
		data, readErr := reader.ReadBytes('\n')
		if readErr != nil && !errors.Is(readErr, io.EOF) {
			return nil, 0, readErr
		}
		complete := readErr == nil
		if len(bytes.TrimSpace(data)) > 0 {
			var record CaseCheckpoint
			if err := json.Unmarshal(data, &record); err != nil {
				if !complete {
					break // torn final line: dropped and truncated away
				}
				return nil, 0, fmt.Errorf("%s line %d: %w", path, line, err)
			}
			records = append(records, record)
			// A whole record whose newline write was lost.
			missingNewline = !complete
		}
		valid += int64(len(data))
		if !complete {
			break
		}
	}
	if missingNewline {
		if err := appendNewline(path); err != nil {
			return nil, 0, err
		}
		valid++
	}
	return records, valid, nil
}

func appendNewline(path string) error {
	file, err := os.OpenFile(path, os.O_WRONLY|os.O_APPEND, 0o600)
	if err != nil {
		return err
	}
	if _, err := file.Write([]byte{'\n'}); err != nil {
		_ = file.Close()
		return err
	}
	return file.Close()
}

// reusable reports a case an earlier attempt already finished validly.
func (c *Checkpoint) reusable(id string) (CaseCheckpoint, bool) {
	if c == nil {
		return CaseCheckpoint{}, false
	}
	record, ok := c.done[id]
	return record, ok
}

// record appends one finished case (fsynced), refreshes progress.json and
// prints the progress line. A write failure is reported once and does not
// stop the run: the final artifacts are still written from memory.
func (c *Checkpoint) record(index int, result CaseResult, trace []TraceRecord, elapsed time.Duration) {
	if c == nil {
		return
	}
	status := caseStatus(result)
	entry := CaseCheckpoint{
		Index:      index,
		CaseID:     result.ID,
		Status:     status,
		ElapsedMS:  elapsed.Milliseconds(),
		FinishedAt: c.now().UTC(),
		Result:     result,
		Trace:      trace,
	}
	line, err := json.Marshal(entry)
	c.mu.Lock()
	defer c.mu.Unlock()
	if err == nil {
		line = append(line, '\n')
		if _, err = c.file.Write(line); err == nil {
			err = c.file.Sync()
		}
	}
	if err != nil && !c.warned {
		c.warned = true
		fmt.Fprintf(c.log, "warning: checkpoint write to %s failed, later cases are not resumable: %v\n", c.dir, err)
	}
	c.progress.Done++
	switch status {
	case CaseStatusPass:
		c.progress.Pass++
	case CaseStatusInvalid:
		c.progress.Invalid++
	default:
		c.progress.Fail++
	}
	c.progress.UpdatedAt = entry.FinishedAt
	etaText := "?"
	c.progress.ETASeconds, c.progress.ETAAt = nil, nil
	if eta, ok := estimateETA(
		c.progress.Done-c.progress.Resumed,
		c.progress.Total-c.progress.Done,
		entry.FinishedAt.Sub(c.progress.AttemptStartedAt),
	); ok {
		seconds := int64(eta / time.Second)
		at := entry.FinishedAt.Add(eta)
		c.progress.ETASeconds, c.progress.ETAAt = &seconds, &at
		etaText = formatETA(eta)
	}
	if err := c.writeProgress(); err != nil && !c.warned {
		c.warned = true
		fmt.Fprintf(c.log, "warning: progress write to %s failed: %v\n", c.dir, err)
	}
	fmt.Fprintf(c.log, "[%d/%d] %s %s %s eta %s\n", c.progress.Done, c.progress.Total, result.ID, status,
		elapsed.Round(time.Second), etaText)
}

// etaMinSamples is how many cases of the current attempt must finish before
// an ETA is shown; the first completions are the shortest cases and would
// promise far too early a finish.
const etaMinSamples = 5

// estimateETA extrapolates this attempt's throughput (finished cases per
// wall-clock second since the attempt started) over the remaining cases.
// Measuring whole-attempt throughput rather than per-case time keeps the
// estimate right under case parallelism. It reads optimistic early on and
// near the end, when the slow cases still in flight dominate.
func estimateETA(finished, remaining int, elapsed time.Duration) (time.Duration, bool) {
	if remaining <= 0 {
		return 0, true
	}
	if finished < etaMinSamples || elapsed <= 0 {
		return 0, false
	}
	return time.Duration(float64(elapsed) / float64(finished) * float64(remaining)), true
}

// formatETA rounds to seconds below ten minutes and to minutes above.
func formatETA(eta time.Duration) string {
	if eta < 10*time.Minute {
		return eta.Round(time.Second).String()
	}
	return strings.TrimSuffix(eta.Round(time.Minute).String(), "0s")
}

// NeedsRerun reports a finished case whose result is not a reading of the
// model: an invalid case, or a turn failure that InfrastructureFailure
// classifies as a transport or provider break (including a case timeout). A
// resumed run executes such cases again instead of reusing them.
func NeedsRerun(result CaseResult) bool {
	if result.Invalid {
		return true
	}
	for _, turn := range result.Turns {
		for _, failure := range turn.Failures {
			if InfrastructureFailure(failure) {
				return true
			}
		}
	}
	return false
}

// InfrastructureFailure reports whether a failure string is a transport or
// provider break rather than a model or protocol score. lab/runs and the
// bench sweep share this rule through runs.InfrastructureFailure.
func InfrastructureFailure(failure string) bool {
	if !strings.HasPrefix(failure, "runner error:") {
		return false
	}
	text := strings.ToLower(failure)
	if strings.Contains(text, "agent protocol error:") {
		return false
	}
	for _, marker := range []string{
		"rwkv_lightning continuation error:", "irwkv continuation error:", "http 4", "http 5",
		"connection refused", "context deadline exceeded", "no such host",
		"timeout", "connection reset", "unexpected eof", "broken pipe",
	} {
		if strings.Contains(text, marker) {
			return true
		}
	}
	return false
}

func caseStatus(result CaseResult) string {
	switch {
	case result.Invalid:
		return CaseStatusInvalid
	case result.Passed:
		return CaseStatusPass
	default:
		return CaseStatusFail
	}
}

// writeProgress replaces progress.json atomically; callers hold c.mu or own c
// exclusively.
func (c *Checkpoint) writeProgress() error {
	data, err := json.MarshalIndent(c.progress, "", "  ")
	if err != nil {
		return err
	}
	temporary := filepath.Join(c.dir, checkpointProgressFile+".tmp")
	if err := os.WriteFile(temporary, append(data, '\n'), 0o600); err != nil {
		return err
	}
	return os.Rename(temporary, filepath.Join(c.dir, checkpointProgressFile))
}

// Dir is the checkpoint directory (<output>.partial).
func (c *Checkpoint) Dir() string {
	if c == nil {
		return ""
	}
	return c.dir
}

// Progress returns a copy of the current progress counters.
func (c *Checkpoint) Progress() CheckpointProgress {
	if c == nil {
		return CheckpointProgress{}
	}
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.progress
}

// Close releases cases.jsonl; the directory stays for a later resume.
func (c *Checkpoint) Close() error {
	if c == nil || c.file == nil {
		return nil
	}
	c.mu.Lock()
	defer c.mu.Unlock()
	err := c.file.Close()
	c.file = nil
	return err
}

// Remove closes the checkpoint and deletes its directory, once the final
// artifacts hold everything it recorded.
func (c *Checkpoint) Remove() error {
	if c == nil {
		return nil
	}
	if err := c.Close(); err != nil {
		return err
	}
	return os.RemoveAll(c.dir)
}

// signatureExcluded lists manifest fields that may change between attempts
// without changing what a case measures: lowering case parallelism after an
// OOM is the point of resuming.
var signatureExcluded = map[string]bool{
	"harness.case_parallelism": true,
}

// RunSignature flattens the result-relevant part of a run manifest into
// comparable entries: suite, every model, harness and sampling field (as
// JSON), and digests of the case IDs, per-case wires and case content. Run
// identity, timestamps and the build environment are not part of it.
func RunSignature(manifest RunManifest) map[string]string {
	signature := map[string]string{
		"suite":      compactJSON(manifest.Suite),
		"case_ids":   digestJSON(manifest.CaseIDs),
		"case_wires": digestJSON(manifest.CaseWires),
		"cases":      digestJSON(manifest.Cases),
	}
	for prefix, value := range map[string]any{
		"model":    manifest.Model,
		"harness":  manifest.Harness,
		"sampling": manifest.Sampling,
	} {
		data, err := json.Marshal(value)
		if err != nil {
			signature[prefix] = "unencodable: " + err.Error()
			continue
		}
		var fields map[string]json.RawMessage
		if err := json.Unmarshal(data, &fields); err != nil {
			signature[prefix] = string(data)
			continue
		}
		for key, raw := range fields {
			name := prefix + "." + key
			if !signatureExcluded[name] {
				signature[name] = string(raw)
			}
		}
	}
	return signature
}

// SignatureDiff lists the entries that differ, as "name: old -> new" lines in
// name order; an entry present on one side only is shown as <unset>.
func SignatureDiff(stored, current map[string]string) []string {
	names := map[string]bool{}
	for name := range stored {
		names[name] = true
	}
	for name := range current {
		names[name] = true
	}
	var diffs []string
	for name := range names {
		before, hadBefore := stored[name]
		after, hasAfter := current[name]
		if hadBefore == hasAfter && before == after {
			continue
		}
		// Long values (wire_canonical) are clipped around the first byte
		// that differs, so the change stays visible.
		common := 0
		for common < len(before) && common < len(after) && before[common] == after[common] {
			common++
		}
		diffs = append(diffs, fmt.Sprintf("%s: %s -> %s",
			name, signatureValue(before, hadBefore, common), signatureValue(after, hasAfter, common)))
	}
	sort.Strings(diffs)
	return diffs
}

func signatureValue(value string, present bool, differsAt int) string {
	if !present {
		return "<unset>"
	}
	const limit = 120
	if len(value) <= limit {
		return value
	}
	start := max(0, differsAt-40)
	end := min(len(value), start+limit)
	clipped := value[start:end]
	if start > 0 {
		clipped = "..." + clipped
	}
	if end < len(value) {
		clipped += "..."
	}
	return clipped
}

func compactJSON(value any) string {
	data, err := json.Marshal(value)
	if err != nil {
		return "unencodable: " + err.Error()
	}
	return string(data)
}

func digestJSON(value any) string {
	data, err := json.Marshal(value)
	if err != nil {
		return "unencodable: " + err.Error()
	}
	sum := sha256.Sum256(data)
	return "sha256:" + hex.EncodeToString(sum[:])
}
