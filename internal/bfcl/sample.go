package bfcl

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math"
	"os"
	"sort"
	"strconv"
	"strings"
)

const (
	SampleManifestSchemaVersion = 1
	SampleAlgorithmVersion      = "bfcl-ab-stratified-hare-v1"
	SampleDocumentLength        = "sum of original function JSON byte lengths"
	SamplePercentileMethod      = "nearest-rank p33/p66; buckets are <=p33, <=p66, >p66"
	SampleToolCountBuckets      = "0-1, 2-4, 5+; zero-tool cases exist only in live_irrelevance"
)

type SampleTarget struct {
	Category string
	Count    int
}

var DefaultSampleTargets = []SampleTarget{
	{Category: "simple_python", Count: 40},
	{Category: "simple_java", Count: 20},
	{Category: "simple_javascript", Count: 15},
	{Category: "multiple", Count: 30},
	{Category: "parallel", Count: 30},
	{Category: "parallel_multiple", Count: 30},
	{Category: "irrelevance", Count: 30},
	{Category: "live_simple", Count: 30},
	{Category: "live_multiple", Count: 40},
	{Category: "live_parallel", Count: 16},
	{Category: "live_parallel_multiple", Count: 24},
	{Category: "live_relevance", Count: 16},
	{Category: "live_irrelevance", Count: 30},
}

type SampleManifest struct {
	SchemaVersion        int           `json:"schema_version"`
	ManifestVersion      string        `json:"manifest_version"`
	DataCommit           string        `json:"data_commit"`
	Algorithm            string        `json:"algorithm"`
	DocumentLength       string        `json:"document_length"`
	PercentileMethod     string        `json:"percentile_method"`
	ToolCountBuckets     string        `json:"tool_count_buckets"`
	SourceManifestSHA256 string        `json:"source_manifest_sha256,omitempty"`
	Splits               []SampleSplit `json:"splits"`
}

type SampleSplit struct {
	Category   string          `json:"category"`
	Population int             `json:"population"`
	SampleSize int             `json:"sample_size"`
	P33Bytes   int             `json:"p33_bytes"`
	P66Bytes   int             `json:"p66_bytes"`
	Strata     []SampleStratum `json:"strata"`
	IDs        []string        `json:"ids"`
}

type SampleStratum struct {
	ToolBucket   int `json:"tool_bucket"`
	LengthBucket int `json:"length_bucket"`
	Population   int `json:"population"`
	SampleSize   int `json:"sample_size"`
}

type sampleKey struct {
	toolBucket   int
	lengthBucket int
}

type sampleItem struct {
	entry  Case
	length int
	key    sampleKey
}

func GenerateSampleManifest(dataDir, dataCommit, version string, targets []SampleTarget) (SampleManifest, error) {
	if strings.TrimSpace(dataCommit) == "" || strings.TrimSpace(version) == "" {
		return SampleManifest{}, fmt.Errorf("BFCL sample data commit and manifest version are required")
	}
	if len(targets) == 0 {
		return SampleManifest{}, fmt.Errorf("BFCL sample targets are required")
	}
	manifest := SampleManifest{
		SchemaVersion:    SampleManifestSchemaVersion,
		ManifestVersion:  version,
		DataCommit:       dataCommit,
		Algorithm:        SampleAlgorithmVersion,
		DocumentLength:   SampleDocumentLength,
		PercentileMethod: SamplePercentileMethod,
		ToolCountBuckets: SampleToolCountBuckets,
		Splits:           make([]SampleSplit, 0, len(targets)),
	}
	seen := make(map[string]struct{}, len(targets))
	for _, target := range targets {
		if _, exists := seen[target.Category]; exists {
			return SampleManifest{}, fmt.Errorf("duplicate BFCL sample target %q", target.Category)
		}
		seen[target.Category] = struct{}{}
		cases, err := LoadSplit(dataDir, target.Category)
		if err != nil {
			return SampleManifest{}, err
		}
		split, err := sampleSplit(cases, target.Count)
		if err != nil {
			return SampleManifest{}, fmt.Errorf("sample BFCL split %q: %w", target.Category, err)
		}
		manifest.Splits = append(manifest.Splits, split)
	}
	return manifest, nil
}

func sampleSplit(cases []Case, sampleSize int) (SampleSplit, error) {
	if len(cases) == 0 || sampleSize <= 0 || sampleSize > len(cases) {
		return SampleSplit{}, fmt.Errorf("invalid sample size %d for population %d", sampleSize, len(cases))
	}
	category := cases[0].Category
	lengths := make([]int, len(cases))
	items := make([]sampleItem, len(cases))
	seen := make(map[string]struct{}, len(cases))
	for index, entry := range cases {
		if entry.Category != category {
			return SampleSplit{}, fmt.Errorf("mixed categories %q and %q", category, entry.Category)
		}
		if _, exists := seen[entry.ID]; exists {
			return SampleSplit{}, fmt.Errorf("duplicate case id %q", entry.ID)
		}
		seen[entry.ID] = struct{}{}
		if _, err := naturalIDSuffix(category, entry.ID); err != nil {
			return SampleSplit{}, err
		}
		for _, function := range entry.Functions {
			lengths[index] += len(function)
		}
		items[index] = sampleItem{entry: entry, length: lengths[index]}
	}
	p33 := nearestRank(lengths, 33)
	p66 := nearestRank(lengths, 66)
	strata := make(map[sampleKey][]sampleItem)
	for index := range items {
		items[index].key = sampleKey{
			toolBucket:   toolCountBucket(len(items[index].entry.Functions)),
			lengthBucket: documentLengthBucket(items[index].length, p33, p66),
		}
		strata[items[index].key] = append(strata[items[index].key], items[index])
	}
	quotas := largestRemainderQuotas(strata, sampleSize, len(cases))
	keys := sortedSampleKeys(strata)
	selected := make([]Case, 0, sampleSize)
	stratumRecords := make([]SampleStratum, 0, len(keys))
	for _, key := range keys {
		entries := strata[key]
		sort.Slice(entries, func(left, right int) bool {
			less, _ := naturalIDLess(category, entries[left].entry.ID, entries[right].entry.ID)
			return less
		})
		quota := quotas[key]
		for sampleIndex := 0; sampleIndex < quota; sampleIndex++ {
			selected = append(selected, entries[sampleIndex*len(entries)/quota].entry)
		}
		stratumRecords = append(stratumRecords, SampleStratum{
			ToolBucket:   key.toolBucket,
			LengthBucket: key.lengthBucket,
			Population:   len(entries),
			SampleSize:   quota,
		})
	}
	if len(selected) != sampleSize {
		return SampleSplit{}, fmt.Errorf("selected %d cases; expected %d", len(selected), sampleSize)
	}
	sort.Slice(selected, func(left, right int) bool {
		less, _ := naturalIDLess(category, selected[left].ID, selected[right].ID)
		return less
	})
	ids := make([]string, len(selected))
	for index, entry := range selected {
		ids[index] = entry.ID
	}
	return SampleSplit{
		Category:   category,
		Population: len(cases),
		SampleSize: sampleSize,
		P33Bytes:   p33,
		P66Bytes:   p66,
		Strata:     stratumRecords,
		IDs:        ids,
	}, nil
}

func nearestRank(values []int, percentile int) int {
	ordered := append([]int(nil), values...)
	sort.Ints(ordered)
	rank := (percentile*len(ordered) + 99) / 100
	return ordered[max(rank-1, 0)]
}

func toolCountBucket(count int) int {
	if count <= 1 {
		return 0
	}
	if count <= 4 {
		return 1
	}
	return 2
}

func documentLengthBucket(length, p33, p66 int) int {
	if length <= p33 {
		return 0
	}
	if length <= p66 {
		return 1
	}
	return 2
}

func largestRemainderQuotas(strata map[sampleKey][]sampleItem, sampleSize, population int) map[sampleKey]int {
	type remainder struct {
		key       sampleKey
		numerator int
	}
	quotas := make(map[sampleKey]int, len(strata))
	remainders := make([]remainder, 0, len(strata))
	allocated := 0
	for key, entries := range strata {
		numerator := sampleSize * len(entries)
		quota := numerator / population
		quotas[key] = quota
		allocated += quota
		remainders = append(remainders, remainder{key: key, numerator: numerator % population})
	}
	sort.Slice(remainders, func(left, right int) bool {
		if remainders[left].numerator != remainders[right].numerator {
			return remainders[left].numerator > remainders[right].numerator
		}
		if remainders[left].key.toolBucket != remainders[right].key.toolBucket {
			return remainders[left].key.toolBucket < remainders[right].key.toolBucket
		}
		return remainders[left].key.lengthBucket < remainders[right].key.lengthBucket
	})
	for index := 0; allocated < sampleSize; index++ {
		quotas[remainders[index].key]++
		allocated++
	}
	return quotas
}

func sortedSampleKeys(strata map[sampleKey][]sampleItem) []sampleKey {
	keys := make([]sampleKey, 0, len(strata))
	for key := range strata {
		keys = append(keys, key)
	}
	sort.Slice(keys, func(left, right int) bool {
		if keys[left].toolBucket != keys[right].toolBucket {
			return keys[left].toolBucket < keys[right].toolBucket
		}
		return keys[left].lengthBucket < keys[right].lengthBucket
	})
	return keys
}

func naturalIDLess(category, left, right string) (bool, error) {
	leftParts, err := naturalIDSuffix(category, left)
	if err != nil {
		return false, err
	}
	rightParts, err := naturalIDSuffix(category, right)
	if err != nil {
		return false, err
	}
	if len(leftParts) != len(rightParts) {
		return false, fmt.Errorf("BFCL ids %q and %q use different suffix shapes", left, right)
	}
	for index := range leftParts {
		if leftParts[index] != rightParts[index] {
			return leftParts[index] < rightParts[index], nil
		}
	}
	return false, nil
}

func naturalIDSuffix(category, id string) ([]int, error) {
	prefix := category + "_"
	if !strings.HasPrefix(id, prefix) {
		return nil, fmt.Errorf("BFCL id %q does not match category %q", id, category)
	}
	rawParts := strings.Split(strings.TrimPrefix(id, prefix), "-")
	if len(rawParts) == 0 {
		return nil, fmt.Errorf("BFCL id %q has no numeric suffix", id)
	}
	parts := make([]int, len(rawParts))
	for index, raw := range rawParts {
		value, err := strconv.Atoi(raw)
		if err != nil || value < 0 {
			return nil, fmt.Errorf("BFCL id %q has invalid numeric suffix", id)
		}
		parts[index] = value
	}
	return parts, nil
}

func MarshalSampleManifest(manifest SampleManifest) ([]byte, error) {
	encoded, err := json.MarshalIndent(manifest, "", "  ")
	if err != nil {
		return nil, err
	}
	return append(encoded, '\n'), nil
}

func WriteSampleManifest(path string, manifest SampleManifest) (string, error) {
	encoded, err := MarshalSampleManifest(manifest)
	if err != nil {
		return "", err
	}
	if err := os.WriteFile(path, encoded, 0o600); err != nil {
		return "", err
	}
	return bytesSHA256(encoded), nil
}

func LoadSampleManifest(path string) (SampleManifest, string, error) {
	encoded, err := os.ReadFile(path)
	if err != nil {
		return SampleManifest{}, "", err
	}
	decoder := json.NewDecoder(bytes.NewReader(encoded))
	decoder.DisallowUnknownFields()
	var manifest SampleManifest
	if err := decoder.Decode(&manifest); err != nil {
		return SampleManifest{}, "", fmt.Errorf("decode BFCL sample manifest: %w", err)
	}
	if manifest.SchemaVersion != SampleManifestSchemaVersion || manifest.Algorithm != SampleAlgorithmVersion {
		return SampleManifest{}, "", fmt.Errorf("unsupported BFCL sample manifest schema/algorithm")
	}
	if err := validateSampleManifest(manifest); err != nil {
		return SampleManifest{}, "", err
	}
	return manifest, bytesSHA256(encoded), nil
}

func validateSampleManifest(manifest SampleManifest) error {
	if manifest.ManifestVersion == "" || manifest.DataCommit == "" || len(manifest.Splits) == 0 {
		return fmt.Errorf("BFCL sample manifest is missing identity fields or splits")
	}
	categories := make(map[string]struct{}, len(manifest.Splits))
	allIDs := make(map[string]struct{})
	for _, split := range manifest.Splits {
		if split.Category == "" || split.Population <= 0 || split.SampleSize <= 0 ||
			split.SampleSize > split.Population || len(split.IDs) != split.SampleSize {
			return fmt.Errorf("invalid BFCL sample split %q counts", split.Category)
		}
		if _, exists := categories[split.Category]; exists {
			return fmt.Errorf("duplicate BFCL sample split %q", split.Category)
		}
		categories[split.Category] = struct{}{}
		stratumPopulation := 0
		stratumSamples := 0
		for _, stratum := range split.Strata {
			if stratum.ToolBucket < 0 || stratum.ToolBucket > 2 || stratum.LengthBucket < 0 ||
				stratum.LengthBucket > 2 || stratum.Population <= 0 || stratum.SampleSize < 0 ||
				stratum.SampleSize > stratum.Population {
				return fmt.Errorf("invalid BFCL sample stratum in %q", split.Category)
			}
			stratumPopulation += stratum.Population
			stratumSamples += stratum.SampleSize
		}
		if stratumPopulation != split.Population || stratumSamples != split.SampleSize {
			return fmt.Errorf("BFCL sample strata do not match split %q counts", split.Category)
		}
		for _, id := range split.IDs {
			if _, err := naturalIDSuffix(split.Category, id); err != nil {
				return err
			}
			if _, exists := allIDs[id]; exists {
				return fmt.Errorf("duplicate BFCL sample id %q", id)
			}
			allIDs[id] = struct{}{}
		}
	}
	return nil
}

func FilterBySampleList(cases []Case, listPath string) ([]Case, error) {
	manifest, _, err := LoadSampleManifest(listPath)
	if err != nil {
		return nil, err
	}
	categories := make(map[string]struct{})
	for _, entry := range cases {
		categories[entry.Category] = struct{}{}
	}
	wanted := make(map[string]struct{})
	for _, split := range manifest.Splits {
		if _, loaded := categories[split.Category]; !loaded {
			continue
		}
		for _, id := range split.IDs {
			if _, exists := wanted[id]; exists {
				return nil, fmt.Errorf("duplicate BFCL sample id %q", id)
			}
			wanted[id] = struct{}{}
		}
	}
	if len(wanted) == 0 {
		return nil, fmt.Errorf("BFCL sample manifest contains no IDs for loaded splits")
	}
	filtered := make([]Case, 0, len(wanted))
	for _, entry := range cases {
		if _, ok := wanted[entry.ID]; ok {
			filtered = append(filtered, entry)
			delete(wanted, entry.ID)
		}
	}
	if len(wanted) != 0 {
		missing := make([]string, 0, len(wanted))
		for id := range wanted {
			missing = append(missing, id)
		}
		sort.Strings(missing)
		return nil, fmt.Errorf("BFCL sample IDs not found in loaded splits: %s", strings.Join(missing, ", "))
	}
	return filtered, nil
}

func ExpandedSampleTargets(manifest SampleManifest, triggered map[string]bool) ([]SampleTarget, error) {
	targets := make([]SampleTarget, 0, len(manifest.Splits))
	for _, split := range manifest.Splits {
		count := split.SampleSize
		if triggered[split.Category] {
			switch {
			case count <= 24:
				count = split.Population
			case count <= 30:
				count *= 2
			default:
				count = int(math.Ceil(float64(count) * 1.5))
			}
			count = min(count, split.Population)
		}
		targets = append(targets, SampleTarget{Category: split.Category, Count: count})
	}
	return targets, nil
}

func bytesSHA256(value []byte) string {
	digest := sha256.Sum256(value)
	return hex.EncodeToString(digest[:])
}
