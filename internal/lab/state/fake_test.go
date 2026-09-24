package state

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"sync"
	"testing"
)

// §6 M4 verifies the state tools against a local fake server that records every
// request: the tools talk to a real endpoint, so their behaviour cannot be
// checked against a recorded run the way the offline tools can. This is the Go
// half of that check; the Python original's requests are recorded in
// runs/migration-baseline/state-probe-fake/requests.jsonl and the two sequences
// are compared there.

type recordedRequest struct {
	Method  string            `json:"method"`
	Path    string            `json:"path"`
	Headers map[string]string `json:"headers"`
	Body    string            `json:"body"`
}

type fakeEndpoint struct {
	mu       sync.Mutex
	requests []recordedRequest
	server   *httptest.Server
}

func newFakeEndpoint(t *testing.T) *fakeEndpoint {
	t.Helper()
	fake := &fakeEndpoint{}
	fake.server = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		body := make([]byte, r.ContentLength)
		if r.ContentLength > 0 {
			if _, err := r.Body.Read(body); err != nil && err.Error() != "EOF" {
				t.Errorf("read body: %v", err)
			}
		}
		headers := map[string]string{}
		for name, values := range r.Header {
			if len(values) > 0 {
				headers[http.CanonicalHeaderKey(name)] = values[0]
			}
		}
		fake.mu.Lock()
		fake.requests = append(fake.requests, recordedRequest{r.Method, r.URL.Path, headers, string(body)})
		fake.mu.Unlock()

		w.Header().Set("Content-Type", "application/json")
		switch {
		case filepath.Base(r.URL.Path) == "state/list":
			json.NewEncoder(w).Encode(map[string]any{"data": []any{}})
		default:
			json.NewEncoder(w).Encode(map[string]any{
				"choices": []any{map[string]any{"message": map[string]any{"content": "FAKE OUTPUT"}}},
			})
		}
	}))
	t.Cleanup(fake.server.Close)
	return fake
}

func (f *fakeEndpoint) snapshot() []recordedRequest {
	f.mu.Lock()
	defer f.mu.Unlock()
	return append([]recordedRequest(nil), f.requests...)
}

// The probe must send one greedy continuation per corpus row per arm, in the
// order the arms are declared, with the state id only on the second arm.
func TestProbeSendsOneRequestPerRowPerArm(t *testing.T) {
	fake := newFakeEndpoint(t)
	t.Setenv("RWKV_LAB_API_URL", fake.server.URL+"/v1")

	dir := t.TempDir()
	corpus := filepath.Join(dir, "train.textonly.jsonl")
	lines := ""
	for i := 0; i < 6; i++ {
		call := fmt.Sprintf(`{"name":"read_file","arguments":{"path":"canary-%d.txt"}}`, i)
		text := "User: go\n\nAssistant: <tool_call>" + call + "</tool_call>"
		line, err := json.Marshal(map[string]string{"text": text})
		if err != nil {
			t.Fatal(err)
		}
		lines += string(line) + "\n"
	}
	if err := os.WriteFile(corpus, []byte(lines), 0o644); err != nil {
		t.Fatal(err)
	}
	creds := filepath.Join(dir, "credentials.json")
	if err := os.WriteFile(creds, []byte(`{"WIRE_CF_ID":"id","WIRE_CF_SECRET":"secret"}`), 0o644); err != nil {
		t.Fatal(err)
	}
	out := filepath.Join(dir, "probe.json")

	if code := RunProbe(ProbeArgs{
		Corpus: corpus, Split: "first", Rows: 3, Stride: 1, StateID: "state-final.pth",
		Credentials: creds, Output: out, MaxTokens: 96,
	}); code != 0 {
		t.Fatalf("RunProbe exit code = %d", code)
	}

	requests := fake.snapshot()
	if len(requests) != 6 {
		t.Fatalf("recorded %d requests, want 6 (3 rows x 2 arms)", len(requests))
	}
	for i, request := range requests {
		if request.Method != "POST" || request.Path != "/v1/batch/completions" {
			t.Errorf("request %d = %s %s, want POST /v1/batch/completions", i+1, request.Method, request.Path)
		}
	}
	var bodies []map[string]any
	for _, request := range requests {
		var body map[string]any
		if err := json.Unmarshal([]byte(request.Body), &body); err != nil {
			t.Fatalf("request body is not JSON: %v", err)
		}
		bodies = append(bodies, body)
	}
	for i := 0; i < 3; i++ {
		if _, hasState := bodies[i]["state_id"]; hasState {
			t.Errorf("zero-state arm request %d carried a state_id", i+1)
		}
		if got := bodies[i+3]["state_id"]; got != "state-final.pth" {
			t.Errorf("state arm request %d state_id = %v, want state-final.pth", i+4, got)
		}
	}
	// The credentials never reach the wire except as the CF Access headers.
	for _, request := range requests {
		for name, value := range request.Headers {
			if name == "Cf-Access-Client-Secret" && value != "secret" {
				t.Errorf("unexpected CF secret header value %q", value)
			}
		}
	}
}
