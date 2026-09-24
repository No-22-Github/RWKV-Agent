package corpus

import (
	"fmt"
	"github.com/no22/RWKV-Agent/internal/lab"
	"github.com/no22/RWKV-Agent/internal/lab/similarity"
)

// Flag distillation cases that are too close to the test bank.
//
// The workbank canary strings live only in descriptions and verify scripts,
// never in model-visible text, so a derived variant (same files, renamed
// numbers, reworded prompt) carries no canary. This gate compares what the
// model sees instead: word shingles of the prompt, line shingles of the
// fixtures, and the distinctive names in either.
//
// Features present in more than --boilerplate of the test cases
// (answer-contract sentences, README.md-style names) are ignored on both
// sides, so shared templates do not read as shared tasks. A candidate is
// flagged when any score reaches its threshold, and the exit status is 1 when
// anything is flagged, so the gate can stop a pipeline.

// DecontamArgs are the `corpus decontam` flags.
type DecontamArgs struct {
	Test            string
	Candidates      string
	Records         string
	PromptThreshold float64
	FilesThreshold  float64
	NamesThreshold  float64
	Boilerplate     float64
	Report          string
}

// RunDecontam is the `corpus decontam` command.
func RunDecontam(args DecontamArgs) int {
	thresholds := map[string]float64{
		"prompt": args.PromptThreshold,
		"files":  args.FilesThreshold,
		"names":  args.NamesThreshold,
	}

	testCases, err := Load(args.Test)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 2
	}
	population := make([]similarity.Features, 0, len(testCases))
	for _, caseObj := range testCases {
		population = append(population, similarity.FeaturesOf(caseObj.AsMap()))
	}
	common := similarity.Boilerplate(population, args.Boilerplate)
	test := make([]testItem, 0, len(testCases))
	for i, caseObj := range testCases {
		test = append(test, testItem{
			id:       mapString(caseObj, "id"),
			features: similarity.Strip(population[i], common),
		})
	}

	var candidates []*lab.OrderedMap
	if args.Candidates != "" {
		candidates, err = Load(args.Candidates)
		if err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
	} else {
		records, err := ReadJSONL(args.Records)
		if err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
		for _, record := range records {
			caseObj, err := RecordToCase(record)
			if err != nil {
				fmt.Fprintln(stderr, err)
				return 2
			}
			candidates = append(candidates, caseObj)
		}
	}

	rows := make([]*lab.OrderedMap, 0, len(candidates))
	var flagged []*lab.OrderedMap
	for _, caseObj := range candidates {
		row := nearest(caseObj, test, common, thresholds)
		rows = append(rows, row)
		if truthy(mapValue(row, "flagged")) {
			flagged = append(flagged, row)
		}
	}
	if args.Report != "" {
		if err := WriteJSONL(args.Report, rows, "x"); err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
	}

	fmt.Printf("decontam: %d candidates vs %d test cases; %d flagged\n",
		len(candidates), len(test), len(flagged))
	for _, kind := range similarity.Kinds {
		count := 0
		for _, row := range rows {
			for _, flaggedKind := range stringSlice(mapValue(row, "flagged")) {
				if flaggedKind == kind {
					count++
				}
			}
		}
		fmt.Printf("  %-6s >= %.2f: %d\n", kind, thresholds[kind], count)
	}
	for i, row := range flagged {
		if i >= 15 {
			break
		}
		flaggedKinds := stringSlice(mapValue(row, "flagged"))
		nearestMap, _ := mapValue(row, "nearest").(*lab.OrderedMap)
		closest := mapString(nearestMap, flaggedKinds[0])
		fmt.Printf("  %s  prompt %.2f  files %.2f  names %.2f  ~ %s\n",
			mapString(row, "id"),
			floatField(row, "prompt"), floatField(row, "files"), floatField(row, "names"),
			closest)
	}
	if len(flagged) > 15 {
		fmt.Printf("  … %d more\n", len(flagged)-15)
	}
	if len(flagged) > 0 {
		return 1
	}
	return 0
}

// testItem is one test-bank case with its features already stripped of the
// bank-wide boilerplate.
type testItem struct {
	id       string
	features similarity.Features
}

// nearest is the best score per kind over the test bank; the first test case
// wins ties.
func nearest(caseObj *lab.OrderedMap, test []testItem, common similarity.Features,
	thresholds map[string]float64) *lab.OrderedMap {

	mine := similarity.Strip(similarity.FeaturesOf(caseObj.AsMap()), common)
	bestValue := map[string]float64{}
	bestID := map[string]string{}
	for _, kind := range similarity.Kinds {
		bestValue[kind] = 0
		bestID[kind] = ""
	}
	for _, item := range test {
		scores := similarity.Scores(mine, item.features)
		for _, kind := range similarity.Kinds {
			if scores[kind] > bestValue[kind] {
				bestValue[kind] = scores[kind]
				bestID[kind] = item.id
			}
		}
	}

	nearestMap := lab.NewOrderedMap()
	for _, kind := range similarity.Kinds {
		nearestMap.Set(kind, bestID[kind])
	}
	var flagged []any
	for _, kind := range similarity.Kinds {
		if bestValue[kind] >= thresholds[kind] {
			flagged = append(flagged, kind)
		}
	}

	row := lab.NewOrderedMap()
	row.Set("id", mapString(caseObj, "id"))
	for _, kind := range similarity.Kinds {
		row.Set(kind, lab.PyFloat(lab.RoundHalfEven(bestValue[kind], 3)))
	}
	row.Set("nearest", nearestMap)
	row.Set("flagged", flagged)
	return row
}

func stringSlice(v any) []string {
	items, _ := v.([]any)
	out := make([]string, 0, len(items))
	for _, item := range items {
		if s, ok := item.(string); ok {
			out = append(out, s)
		}
	}
	return out
}

func floatField(m *lab.OrderedMap, key string) float64 {
	v, _ := m.Get(key)
	f, _ := asFloat64(v)
	return f
}
