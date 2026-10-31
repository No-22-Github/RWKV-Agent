package geval

import (
	"bufio"
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"net/http"
	"net/textproto"
	"os"
	"os/signal"
	"path/filepath"
	"reflect"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/no22/RWKV-Agent/internal/buildinfo"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/provider"
	"github.com/no22/RWKV-Agent/internal/lab"
	"github.com/no22/RWKV-Agent/internal/samplingpreset"
)

// completionChat drives a chat-template model (Qwen) through its own
// template; thinking comes back as reasoning_content.
const completionChat = "chat-completions"

// RunConfig is what a run was made with. A resume must match it exactly
// (Created and Commit aside).
type RunConfig struct {
	Items        string   `json:"items"`
	ItemsSHA256  string   `json:"items_sha256"`
	Subset       string   `json:"subset"`
	Tasks        []string `json:"tasks,omitempty"`
	Limit        int      `json:"limit,omitempty"`
	Completion   string   `json:"completion"`
	APIURL       string   `json:"api_url"`
	Model        string   `json:"model"`
	AdapterID    string   `json:"adapter_id,omitempty"`
	StateID      string   `json:"state_id,omitempty"`
	StopTokens   string   `json:"stop_tokens,omitempty"`
	Sampling     string   `json:"sampling"`
	SamplingVals any      `json:"sampling_values"`
	MaxTokens    int      `json:"max_tokens"`
	LoopGuard    bool     `json:"loop_guard"`
	ChatThinking bool     `json:"chat_thinking,omitempty"`
	Format       string   `json:"format"`
	Created      string   `json:"created"`
	Commit       string   `json:"commit"`
}

// TurnRecord is one generation.
type TurnRecord struct {
	Prompt           string `json:"prompt"`
	Raw              string `json:"raw"`
	Think            string `json:"think"`
	Answer           string `json:"answer"`
	ThinkClosed      bool   `json:"think_closed"`
	EmptyThink       bool   `json:"empty_think"`
	Finish           string `json:"finish"`
	PromptTokens     int    `json:"prompt_tokens"`
	CompletionTokens int    `json:"completion_tokens"`
	Loop             bool   `json:"loop"`
	Millis           int64  `json:"ms"`
}

// Record is one item's result line in results.jsonl. A later line for the
// same id replaces an earlier one.
type Record struct {
	ID    string       `json:"id"`
	Task  string       `json:"task"`
	Turns []TurnRecord `json:"turns"`
	Error string       `json:"error,omitempty"`
	At    string       `json:"at"`
}

type generator interface {
	generate(ctx context.Context, history []Exchange, user string) (TurnRecord, error)
}

type rwkvGenerator struct {
	gen       continuation.Generator
	model     string
	maxTokens int
	sampling  continuation.Sampling
}

func (g rwkvGenerator) generate(ctx context.Context, history []Exchange, user string) (TurnRecord, error) {
	prompt := renderPrompt(history, user)
	start := time.Now()
	res, err := g.gen.Continue(ctx, continuation.Request{
		Model: g.model, Prompt: prompt, MaxOutputTokens: g.maxTokens,
		Stops: []string{turnStop}, Sampling: g.sampling,
	}, nil)
	if err != nil {
		return TurnRecord{}, err
	}
	raw := thinkSeed + res.Text
	return finishTurn(TurnRecord{
		Prompt: prompt, Raw: raw, Finish: string(res.FinishReason),
		PromptTokens: res.Usage.PromptTokens, CompletionTokens: res.Usage.CompletionTokens,
		Millis: time.Since(start).Milliseconds(),
	}), nil
}

type chatGenerator struct {
	client *chatClient
	params map[string]any
}

func (g chatGenerator) generate(ctx context.Context, history []Exchange, user string) (TurnRecord, error) {
	var messages []chatMessage
	for _, h := range history {
		messages = append(messages, chatMessage{"user", h.User}, chatMessage{"assistant", h.Answer})
	}
	messages = append(messages, chatMessage{"user", user})
	start := time.Now()
	reply, err := g.client.complete(ctx, messages, g.params)
	if err != nil {
		return TurnRecord{}, fmt.Errorf("%w: %v", continuation.ErrUpstream, err)
	}
	content := reply.Content
	think := reply.Reasoning
	if think == "" {
		// Templates that leave the think block in the content.
		if i := strings.Index(content, thinkClose); i >= 0 {
			think = strings.TrimPrefix(strings.TrimSpace(content[:i]), thinkOpen)
			content = content[i+len(thinkClose):]
		}
	}
	prompt, _ := json.Marshal(messages)
	return finishTurn(TurnRecord{
		Prompt: string(prompt), Raw: thinkOpen + think + thinkClose + "\n" + content,
		Finish: reply.FinishReason, PromptTokens: reply.PromptTokens, CompletionTokens: reply.CompletionTokens,
		Millis: time.Since(start).Milliseconds(),
	}), nil
}

func finishTurn(t TurnRecord) TurnRecord {
	p := parseOutput(t.Raw)
	t.Think, t.Answer, t.ThinkClosed, t.EmptyThink = p.Think, p.Answer, p.ThinkClosed, p.EmptyThink
	guard := continuation.NewLoopGuard()
	t.Loop = guard.Write(t.Raw)
	return t
}

type headerFlags []string

func (h *headerFlags) String() string     { return strings.Join(*h, ",") }
func (h *headerFlags) Set(v string) error { *h = append(*h, v); return nil }

func runRun(args []string) int {
	flags := flag.NewFlagSet("rwkv-lab geval run", flag.ContinueOnError)
	itemsPath := flags.String("items", DefaultItemsPath(), "items file")
	subset := flags.String("subset", "quick", "quick | full")
	tasks := flags.String("tasks", "", "comma-separated task filter (default all)")
	limit := flags.Int("limit", 0, "at most this many items per task (debugging)")
	out := flags.String("out", "", "run directory (required)")
	completion := flags.String("completion", provider.IRWKV, "rwkv-lightning-cuda | irwkv | chat-completions")
	apiURL := flags.String("api-url", "", "inference endpoint, up to /v1")
	model := flags.String("model", "", "model id")
	apiKeyEnv := flags.String("api-key-env", "", "environment variable holding a Bearer key (irwkv, chat-completions)")
	passwordEnv := flags.String("api-password-env", "", "environment variable holding the rwkv_lightning password")
	var headerEnvs headerFlags
	flags.Var(&headerEnvs, "api-header-env", "HEADER=ENV extra request header (repeatable)")
	adapterID := flags.String("adapter-id", "", "rwkv_lightning adapter (MiSS/NoRA) id bound to every generation")
	stateID := flags.String("state-id", "", "rwkv_lightning uploaded state id")
	stopTokens := flags.String("stop-tokens", "0,24281", "RWKV stop token ids (EOS and User); text stop \\n\\nUser: is always applied")
	sampling := flags.String("sampling", samplingpreset.AgentFast, "named sampling preset ("+strings.Join(samplingpreset.Names(), ", ")+")")
	maxTokens := flags.Int("max-tokens", 8192, "generation budget per turn (thinking included)")
	parallel := flags.Int("parallel", 32, "items in flight")
	batchInflight := flags.Int("batch-inflight", 4, "rwkv_lightning coalesced requests in flight (cards behind the endpoint)")
	loopGuard := flags.Bool("loop-guard", true, "end a generation early once it loops verbatim")
	chatThinking := flags.Bool("chat-thinking", true, "chat-completions: send chat_template_kwargs.enable_thinking")
	if err := flags.Parse(args); err != nil {
		return 2
	}
	if *out == "" || *apiURL == "" || *model == "" {
		fmt.Fprintln(os.Stderr, "rwkv-lab geval run: --out, --api-url and --model are required")
		return 2
	}
	preset, ok := samplingpreset.Lookup(*sampling)
	if !ok {
		fmt.Fprintf(os.Stderr, "rwkv-lab geval run: unknown sampling preset %q\n", *sampling)
		return 2
	}
	items, sha, err := loadItems(*itemsPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab geval run:", err)
		return 1
	}
	selected, err := selectItems(items, *subset, *tasks, *limit)
	if err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab geval run:", err)
		return 2
	}
	commit, dirty := buildinfo.Revision()
	if dirty {
		commit += "-dirty"
	}
	cfg := RunConfig{
		Items: *itemsPath, ItemsSHA256: sha, Subset: *subset, Limit: *limit,
		Completion: *completion, APIURL: *apiURL, Model: *model, AdapterID: *adapterID, StateID: *stateID,
		Sampling: samplingpreset.CanonicalName(*sampling), SamplingVals: preset, MaxTokens: *maxTokens,
		LoopGuard: *loopGuard, Format: "think-sft (User/Assistant, prompt ends `<think`, history `<think></think>`)",
		Created: time.Now().Format(time.RFC3339), Commit: commit,
	}
	if *tasks != "" {
		cfg.Tasks = strings.Split(*tasks, ",")
	}
	var gen generator
	if *completion == completionChat {
		cfg.ChatThinking = *chatThinking
		cfg.Format = "chat template (" + *completion + ")"
		params := map[string]any{
			"max_tokens": *maxTokens, "temperature": preset.Temperature, "top_p": preset.TopP,
			"presence_penalty": preset.PresencePenalty, "frequency_penalty": preset.FrequencyPenalty,
		}
		if preset.TopK != samplingpreset.NoTruncation {
			params["top_k"] = preset.TopK
		}
		gen = chatGenerator{client: newChatClient(*apiURL, *model, os.Getenv(*apiKeyEnv),
			map[string]any{"chat_template_kwargs": map[string]any{"enable_thinking": *chatThinking}}), params: params}
	} else {
		cfg.StopTokens = *stopTokens
		headers, err := loadHeaders(headerEnvs)
		if err != nil {
			fmt.Fprintln(os.Stderr, "rwkv-lab geval run:", err)
			return 2
		}
		credential := ""
		if *completion == provider.IRWKV && *apiKeyEnv != "" {
			credential = os.Getenv(*apiKeyEnv)
		} else if *passwordEnv != "" {
			credential = os.Getenv(*passwordEnv)
		}
		pc := provider.Config{
			Kind: *completion, Endpoint: *apiURL, Model: *model, Credential: credential, Headers: headers,
			StopTokens: *stopTokens, StateID: *stateID, AdapterID: *adapterID, LoopGuard: *loopGuard,
		}
		if provider.IsLightning(*completion) {
			pc.BatchWait, pc.BatchMax, pc.BatchInflight = 20*time.Millisecond, 64, *batchInflight
		}
		client, err := provider.NewRemote(pc)
		if err != nil {
			fmt.Fprintln(os.Stderr, "rwkv-lab geval run:", err)
			return 2
		}
		gen = rwkvGenerator{gen: client, model: *model, maxTokens: *maxTokens, sampling: continuation.Sampling{
			Temperature: float32(preset.Temperature), TopK: preset.TopK, TopP: float32(preset.TopP),
			PresencePenalty: float32(preset.PresencePenalty), FrequencyPenalty: float32(preset.FrequencyPenalty),
			PenaltyDecay: float32(preset.PenaltyDecay),
		}}
	}
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	if err := execute(ctx, *out, cfg, selected, gen, *parallel); err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab geval run:", err)
		return 1
	}
	return 0
}

func loadHeaders(mappings []string) (http.Header, error) {
	headers := http.Header{}
	for _, m := range mappings {
		name, env, ok := strings.Cut(m, "=")
		if !ok || name == "" || env == "" {
			return nil, fmt.Errorf("invalid --api-header-env %q; expected HEADER=ENV", m)
		}
		value, exists := os.LookupEnv(env)
		if !exists {
			return nil, fmt.Errorf("--api-header-env %s: %s is not set", name, env)
		}
		headers.Set(textproto.CanonicalMIMEHeaderKey(name), value)
	}
	return headers, nil
}

func selectItems(items []Item, subset, tasks string, limit int) ([]Item, error) {
	if subset != "quick" && subset != "full" {
		return nil, fmt.Errorf("--subset must be quick or full, not %q", subset)
	}
	want := map[string]bool{}
	for _, t := range strings.Split(tasks, ",") {
		if t = strings.TrimSpace(t); t != "" {
			want[t] = true
		}
	}
	per := map[string]int{}
	var out []Item
	for _, item := range items {
		if subset == "quick" && !item.Quick {
			continue
		}
		if len(want) > 0 && !want[item.Task] {
			continue
		}
		if limit > 0 && per[item.Task] >= limit {
			continue
		}
		per[item.Task]++
		out = append(out, item)
	}
	if len(out) == 0 {
		return nil, fmt.Errorf("no items selected")
	}
	return out, nil
}

// execute generates every selected item not already done in dir, appending
// one line per item to results.jsonl.
func execute(ctx context.Context, dir string, cfg RunConfig, items []Item, gen generator, parallel int) error {
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return err
	}
	if err := checkOrWriteConfig(dir, cfg); err != nil {
		return err
	}
	done, err := loadRecords(filepath.Join(dir, "results.jsonl"))
	if err != nil {
		return err
	}
	var todo []Item
	for _, item := range items {
		if r, ok := done[item.ID]; !ok || r.Error != "" {
			todo = append(todo, item)
		}
	}
	fmt.Printf("geval run: %d items, %d done, %d to go → %s\n", len(items), len(items)-len(todo), len(todo), dir)
	if len(todo) == 0 {
		return nil
	}
	fh, err := os.OpenFile(filepath.Join(dir, "results.jsonl"), os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	defer fh.Close()
	if err := endWithNewline(fh); err != nil {
		return err
	}
	var mu sync.Mutex
	finished, failed := 0, 0
	start := time.Now()
	write := func(rec Record) error {
		line, err := lab.EncodeJSON(rec, 0)
		if err != nil {
			return err
		}
		mu.Lock()
		defer mu.Unlock()
		if _, err := fh.Write(append(line, '\n')); err != nil {
			return err
		}
		finished++
		status := "ok"
		if rec.Error != "" {
			failed++
			status = "ERR " + truncate(rec.Error, 120)
		}
		elapsed := time.Since(start)
		eta := time.Duration(float64(elapsed) / float64(finished) * float64(len(todo)-finished))
		fmt.Printf("[%d/%d] %s %s  %s eta %s\n", finished, len(todo), rec.ID, status,
			elapsed.Round(time.Second), eta.Round(time.Second))
		return fh.Sync()
	}
	jobs := make(chan Item)
	errs := make(chan error, parallel)
	var wg sync.WaitGroup
	for w := 0; w < parallel; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for item := range jobs {
				rec := runItem(ctx, gen, item)
				if ctx.Err() != nil {
					return
				}
				if err := write(rec); err != nil {
					errs <- err
					return
				}
			}
		}()
	}
feed:
	for _, item := range todo {
		select {
		case jobs <- item:
		case <-ctx.Done():
			break feed
		case err := <-errs:
			close(jobs)
			wg.Wait()
			return err
		}
	}
	close(jobs)
	wg.Wait()
	if ctx.Err() != nil {
		return fmt.Errorf("interrupted after %d items; rerun the same command to resume", finished)
	}
	if failed > 0 {
		fmt.Printf("geval run: %d items failed; rerun the same command to retry them\n", failed)
	}
	return nil
}

// retryDelay is the backoff step between attempts at one turn.
var retryDelay = 5 * time.Second

// runItem generates every turn of one item, retrying upstream failures.
func runItem(ctx context.Context, gen generator, item Item) Record {
	rec := Record{ID: item.ID, Task: item.Task}
	var history []Exchange
	for _, user := range item.Turns {
		var turn TurnRecord
		var err error
		for attempt := 0; attempt < 3; attempt++ {
			if attempt > 0 {
				select {
				case <-ctx.Done():
				case <-time.After(time.Duration(attempt) * retryDelay):
				}
			}
			turn, err = gen.generate(ctx, history, user)
			if err == nil || ctx.Err() != nil || errors.Is(err, continuation.ErrInvalidRequest) {
				break
			}
		}
		if err != nil {
			rec.Error = err.Error()
			break
		}
		rec.Turns = append(rec.Turns, turn)
		history = append(history, Exchange{User: user, Answer: turn.Answer})
	}
	rec.At = time.Now().Format(time.RFC3339)
	return rec
}

// endWithNewline terminates a last line cut short by a kill, so the next
// record does not glue onto it.
func endWithNewline(fh *os.File) error {
	info, err := fh.Stat()
	if err != nil || info.Size() == 0 {
		return err
	}
	last := make([]byte, 1)
	r, err := os.Open(fh.Name())
	if err != nil {
		return err
	}
	defer r.Close()
	if _, err := r.ReadAt(last, info.Size()-1); err != nil {
		return err
	}
	if last[0] != '\n' {
		_, err = fh.Write([]byte{'\n'})
	}
	return err
}

func checkOrWriteConfig(dir string, cfg RunConfig) error {
	path := filepath.Join(dir, "run.json")
	if data, err := os.ReadFile(path); err == nil {
		var old RunConfig
		if err := json.Unmarshal(data, &old); err != nil {
			return fmt.Errorf("%s: %w", path, err)
		}
		a, b := configKey(old), configKey(cfg)
		if !reflect.DeepEqual(a, b) {
			return fmt.Errorf("RESUME REFUSED: %s was made with a different configuration\n  old: %s\n  new: %s", path, a, b)
		}
		return nil
	}
	data, err := lab.EncodeJSON(cfg, 2)
	if err != nil {
		return err
	}
	return os.WriteFile(path, append(data, '\n'), 0o644)
}

// configKey is the config without the fields a resume may change, as
// JSON so decoded and fresh values compare alike.
func configKey(cfg RunConfig) string {
	cfg.Created, cfg.Commit = "", ""
	data, _ := json.Marshal(cfg)
	var v any
	_ = json.Unmarshal(data, &v)
	data, _ = json.Marshal(v)
	return string(data)
}

func loadRecords(path string) (map[string]Record, error) {
	out := map[string]Record{}
	fh, err := os.Open(path)
	if errors.Is(err, os.ErrNotExist) {
		return out, nil
	}
	if err != nil {
		return nil, err
	}
	defer fh.Close()
	scanner := bufio.NewScanner(fh)
	scanner.Buffer(make([]byte, 1<<20), 256<<20)
	for n := 1; scanner.Scan(); n++ {
		line := scanner.Bytes()
		if len(line) == 0 {
			continue
		}
		var rec Record
		if err := json.Unmarshal(line, &rec); err != nil {
			// A line cut by a kill mid-write; the item reruns.
			fmt.Fprintf(os.Stderr, "geval: %s:%d unreadable, skipped\n", path, n)
			continue
		}
		out[rec.ID] = rec
	}
	return out, scanner.Err()
}
