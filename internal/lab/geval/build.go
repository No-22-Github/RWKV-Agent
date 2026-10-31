package geval

import (
	"crypto/sha256"
	"encoding/csv"
	"flag"
	"fmt"
	"math/rand/v2"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// Seed fixes every sample. Changing it is a new Version.
const Seed = 20261031

// Full-set sizes per task; zero takes the whole source.
var fullSize = map[string]int{
	TaskGSM8K:   500,
	TaskMATH500: 200,
	TaskCEval:   250,
	TaskCMMLU:   250,
}

const (
	mathSuffix = "\nPlease reason step by step, and put your final answer within \\boxed{}."
	mcqHeader  = "以下是一道单项选择题，请选出正确答案。\n"
	mcqSuffix  = "\n请在回答的最后一行写出“答案：”加选项字母。"
)

// mtbenchRefCategories are the categories FastChat grades against a
// reference answer (NEED_REF_CATS).
var mtbenchRefCategories = map[string]bool{"math": true, "reasoning": true, "coding": true}

func runBuild(args []string) int {
	flags := flag.NewFlagSet("rwkv-lab geval build", flag.ContinueOnError)
	raw := flags.String("raw", filepath.Join(lab.RepoRoot(), "local", "datasets", "general-eval"), "directory written by bench/general-eval/tools/fetch_raw.py")
	out := flags.String("out", DefaultItemsPath(), "items file to write")
	if err := flags.Parse(args); err != nil {
		return 2
	}
	items, err := buildItems(*raw)
	if err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab geval build:", err)
		return 1
	}
	if err := writeItems(*out, items); err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab geval build:", err)
		return 1
	}
	if err := writeJudgePrompts(*raw, filepath.Join(filepath.Dir(*out), "judge_prompts.json")); err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab geval build:", err)
		return 1
	}
	full, quick := map[string]int{}, map[string]int{}
	for _, item := range items {
		full[item.Task]++
		if item.Quick {
			quick[item.Task]++
		}
	}
	fmt.Println("| task | full | quick |")
	fmt.Println("|---|---:|---:|")
	nf, nq := 0, 0
	for _, task := range taskOrder {
		fmt.Printf("| %s | %d | %d |\n", task, full[task], quick[task])
		nf += full[task]
		nq += quick[task]
	}
	fmt.Printf("| total | %d | %d |\n", nf, nq)
	fmt.Println("wrote", *out)
	return 0
}

func buildItems(raw string) ([]Item, error) {
	var all []Item
	for _, step := range []func(string) ([]Item, error){
		ifevalEN, ifevalZH, mtbenchEN, mtbenchZH, gsm8k, math500, ceval, cmmlu,
	} {
		items, err := step(raw)
		if err != nil {
			return nil, err
		}
		if len(items) == 0 {
			return nil, fmt.Errorf("a source produced no items")
		}
		task := items[0].Task
		if n := fullSize[task]; n > 0 {
			items = stratifiedSample(items, n, rngFor(task, "full"))
		}
		for _, i := range stratifiedSample(items, (len(items)+1)/3, rngFor(task, "quick")) {
			for j := range items {
				if items[j].ID == i.ID {
					items[j].Quick = true
				}
			}
		}
		sort.SliceStable(items, func(a, b int) bool { return idLess(items[a].ID, items[b].ID) })
		all = append(all, items...)
	}
	return all, nil
}

// rngFor seeds one generator per (task, purpose), so adding a task or
// resizing one leaves every other sample unchanged.
func rngFor(task, purpose string) *rand.Rand {
	sum := sha256.Sum256([]byte(fmt.Sprintf("%d/%s/%s", Seed, task, purpose)))
	var a, b uint64
	for i := 0; i < 8; i++ {
		a = a<<8 | uint64(sum[i])
		b = b<<8 | uint64(sum[8+i])
	}
	return rand.New(rand.NewPCG(a, b))
}

// stratifiedSample takes k items, split across strata in proportion to
// their size (largest remainder, ties by stratum name), each stratum's share
// drawn uniformly. Items without a stratum form one stratum.
func stratifiedSample(items []Item, k int, rng *rand.Rand) []Item {
	if k >= len(items) {
		return append([]Item(nil), items...)
	}
	groups := map[string][]Item{}
	var names []string
	for _, item := range items {
		if _, ok := groups[item.Stratum]; !ok {
			names = append(names, item.Stratum)
		}
		groups[item.Stratum] = append(groups[item.Stratum], item)
	}
	sort.Strings(names)
	type share struct {
		name string
		n    int
		rem  float64
	}
	shares := make([]share, len(names))
	total := 0
	for i, name := range names {
		exact := float64(k) * float64(len(groups[name])) / float64(len(items))
		shares[i] = share{name, int(exact), exact - float64(int(exact))}
		total += int(exact)
	}
	order := make([]int, len(shares))
	for i := range order {
		order[i] = i
	}
	sort.SliceStable(order, func(a, b int) bool { return shares[order[a]].rem > shares[order[b]].rem })
	for i := 0; total < k; i++ {
		shares[order[i%len(order)]].n++
		total++
	}
	var out []Item
	for _, s := range shares {
		group := append([]Item(nil), groups[s.name]...)
		rng.Shuffle(len(group), func(a, b int) { group[a], group[b] = group[b], group[a] })
		out = append(out, group[:s.n]...)
	}
	return out
}

// idLess orders "task/12" before "task/100".
func idLess(a, b string) bool {
	pa, na := splitID(a)
	pb, nb := splitID(b)
	if pa != pb {
		return pa < pb
	}
	if na != nb {
		return na < nb
	}
	return a < b
}

func splitID(id string) (string, int) {
	i := strings.LastIndexByte(id, '/')
	if i < 0 {
		return id, 0
	}
	n, err := strconv.Atoi(id[i+1:])
	if err != nil {
		return id, 0
	}
	return id[:i], n
}

func ifevalEN(raw string) ([]Item, error) {
	return ifevalItems(filepath.Join(raw, "ifeval", "ifeval_input_data.jsonl"), TaskIFEvalEN, "en", "google/IFEval")
}

func ifevalZH(raw string) ([]Item, error) {
	return ifevalItems(filepath.Join(raw, "marco-mif", "zh_local.jsonl"), TaskIFEvalZH, "zh", "ATH-MaaS/Marco-Bench-MIF:zh_local")
}

func ifevalItems(path, task, lang, source string) ([]Item, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var items []Item
	for n, line := range lab.SplitJSONLLines(string(data)) {
		if strings.TrimSpace(line) == "" {
			continue
		}
		row, err := decodeRow([]byte(line))
		if err != nil {
			// zh_local.jsonl key 181 has unescaped quotes around "\n\n".
			row, err = decodeRow([]byte(strings.ReplaceAll(line, `（"\n\n"）`, `（\"\\n\\n\"）`)))
			if err != nil {
				return nil, fmt.Errorf("%s:%d: %w", path, n+1, err)
			}
		}
		key := lab.StringOf(row, "key")
		if key == "" {
			key = fmt.Sprint(row["key"])
		}
		prompt, _ := row["prompt"].(string)
		item := Item{
			ID: task + "/" + key, Task: task, Lang: lang, Source: source + "#" + key,
			Turns: []string{prompt}, Raw: prompt,
		}
		for _, id := range row["instruction_id_list"].([]any) {
			item.Instructions = append(item.Instructions, id.(string))
		}
		for _, kw := range row["kwargs"].([]any) {
			clean := map[string]any{}
			for k, v := range kw.(map[string]any) {
				if v != nil {
					clean[k] = v
				}
			}
			item.Kwargs = append(item.Kwargs, clean)
		}
		if len(item.Kwargs) != len(item.Instructions) {
			return nil, fmt.Errorf("%s: %s has %d instructions but %d kwargs", path, item.ID, len(item.Instructions), len(item.Kwargs))
		}
		items = append(items, item)
	}
	return items, nil
}

func mtbenchEN(raw string) ([]Item, error) {
	rows, err := readJSONL(filepath.Join(raw, "mtbench", "question.jsonl"))
	if err != nil {
		return nil, err
	}
	refs, err := mtbenchRefs(filepath.Join(raw, "mtbench", "gpt-4.jsonl"))
	if err != nil {
		return nil, err
	}
	return mtbenchItems(rows, refs, "prompt", TaskMTBenchEN, "en", "HuggingFaceH4/mt_bench_prompts")
}

func mtbenchZH(raw string) ([]Item, error) {
	rows, err := readJSONL(filepath.Join(raw, "mtbench-zh", "question.jsonl"))
	if err != nil {
		return nil, err
	}
	refs, err := mtbenchRefs(filepath.Join(raw, "mtbench-zh", "gpt-4.jsonl"))
	if err != nil {
		return nil, err
	}
	return mtbenchItems(rows, refs, "turns", TaskMTBenchZH, "zh", "GeneZC/MT-Bench-ZH")
}

func mtbenchRefs(path string) (map[string][]string, error) {
	rows, err := readJSONL(path)
	if err != nil {
		return nil, err
	}
	refs := map[string][]string{}
	for _, row := range rows {
		choices := row["choices"].([]any)
		var turns []string
		for _, t := range choices[0].(map[string]any)["turns"].([]any) {
			turns = append(turns, t.(string))
		}
		refs[fmt.Sprint(row["question_id"])] = turns
	}
	return refs, nil
}

func mtbenchItems(rows []map[string]any, refs map[string][]string, turnsKey, task, lang, source string) ([]Item, error) {
	var items []Item
	for _, row := range rows {
		qid := fmt.Sprint(row["question_id"])
		category, _ := row["category"].(string)
		var turns []string
		for _, t := range row[turnsKey].([]any) {
			turns = append(turns, t.(string))
		}
		item := Item{
			ID: task + "/" + qid, Task: task, Lang: lang, Stratum: category, Source: source + "#" + qid,
			Turns: turns, Raw: strings.Join(turns, "\n"),
		}
		if mtbenchRefCategories[category] {
			ref, ok := refs[qid]
			if !ok || len(ref) != len(turns) {
				return nil, fmt.Errorf("%s: no reference answer for %s", task, qid)
			}
			item.Reference = ref
		}
		items = append(items, item)
	}
	return items, nil
}

func gsm8k(raw string) ([]Item, error) {
	rows, err := readJSONL(filepath.Join(raw, "gsm8k", "test.jsonl"))
	if err != nil {
		return nil, err
	}
	var items []Item
	for i, row := range rows {
		q := row["question"].(string)
		answer := row["answer"].(string)
		j := strings.LastIndex(answer, "####")
		if j < 0 {
			return nil, fmt.Errorf("gsm8k row %d has no #### answer", i)
		}
		gold := strings.ReplaceAll(strings.TrimSpace(answer[j+4:]), ",", "")
		items = append(items, Item{
			ID: fmt.Sprintf("%s/%d", TaskGSM8K, i), Task: TaskGSM8K, Lang: "en",
			Source: fmt.Sprintf("openai/gsm8k:main/test#%d", i),
			Turns:  []string{q + mathSuffix}, Raw: q, Answer: gold,
		})
	}
	return items, nil
}

func math500(raw string) ([]Item, error) {
	rows, err := readJSONL(filepath.Join(raw, "math500", "test.jsonl"))
	if err != nil {
		return nil, err
	}
	var items []Item
	for i, row := range rows {
		q := row["problem"].(string)
		items = append(items, Item{
			ID: fmt.Sprintf("%s/%d", TaskMATH500, i), Task: TaskMATH500, Lang: "en",
			Stratum: "level-" + fmt.Sprint(row["level"]),
			Source:  "HuggingFaceH4/MATH-500#" + lab.StringOf(row, "unique_id"),
			Turns:   []string{q + mathSuffix}, Raw: q, Answer: row["answer"].(string),
		})
	}
	return items, nil
}

func mcqItem(task, id, source, subject, question string, options [4]string, answer string) Item {
	var body strings.Builder
	body.WriteString(strings.TrimSpace(question))
	for i, opt := range options {
		fmt.Fprintf(&body, "\n%c. %s", 'A'+i, strings.TrimSpace(opt))
	}
	return Item{
		ID: id, Task: task, Lang: "zh", Stratum: subject, Source: source,
		Turns:  []string{mcqHeader + body.String() + mcqSuffix},
		Raw:    body.String(),
		Answer: strings.TrimSpace(answer),
	}
}

func ceval(raw string) ([]Item, error) {
	rows, err := readJSONL(filepath.Join(raw, "ceval", "val.jsonl"))
	if err != nil {
		return nil, err
	}
	var items []Item
	for i, row := range rows {
		subject := row["subject"].(string)
		items = append(items, mcqItem(TaskCEval, fmt.Sprintf("%s/%d", TaskCEval, i),
			fmt.Sprintf("ceval/ceval-exam:%s/val#%v", subject, row["id"]), subject,
			row["question"].(string),
			[4]string{fmt.Sprint(row["A"]), fmt.Sprint(row["B"]), fmt.Sprint(row["C"]), fmt.Sprint(row["D"])},
			row["answer"].(string)))
	}
	return items, nil
}

func cmmlu(raw string) ([]Item, error) {
	files, err := filepath.Glob(filepath.Join(raw, "cmmlu", "test", "*.csv"))
	if err != nil {
		return nil, err
	}
	sort.Strings(files)
	var items []Item
	for _, path := range files {
		subject := strings.TrimSuffix(filepath.Base(path), ".csv")
		fh, err := os.Open(path)
		if err != nil {
			return nil, err
		}
		records, err := csv.NewReader(fh).ReadAll()
		fh.Close()
		if err != nil {
			return nil, fmt.Errorf("%s: %w", path, err)
		}
		for _, rec := range records[1:] {
			if len(rec) != 7 {
				return nil, fmt.Errorf("%s: row has %d fields", path, len(rec))
			}
			items = append(items, mcqItem(TaskCMMLU, fmt.Sprintf("%s/%d", TaskCMMLU, len(items)),
				fmt.Sprintf("haonan-li/cmmlu:%s/test#%s", subject, rec[0]), subject,
				rec[1], [4]string{rec[2], rec[3], rec[4], rec[5]}, rec[6]))
		}
	}
	return items, nil
}

// writeJudgePrompts copies FastChat's single-answer judge prompts (English)
// and MT-Bench-ZH's (Chinese) next to the items, so scoring needs only bench/.
func writeJudgePrompts(raw, out string) error {
	all := map[string]map[string]map[string]any{}
	for lang, path := range map[string]string{
		"en": filepath.Join(raw, "mtbench", "judge_prompts.jsonl"),
		"zh": filepath.Join(raw, "mtbench-zh", "judge_prompts_zh.jsonl"),
	} {
		rows, err := readJSONL(path)
		if err != nil {
			return err
		}
		all[lang] = map[string]map[string]any{}
		for _, row := range rows {
			name, _ := row["name"].(string)
			if strings.HasPrefix(name, "single-") {
				all[lang][name] = row
			}
		}
	}
	data, err := lab.EncodeJSON(all, 2)
	if err != nil {
		return err
	}
	return os.WriteFile(out, append(data, '\n'), 0o644)
}
