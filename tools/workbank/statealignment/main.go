// statealignment compares every training generation prefix with the production
// renderer, including assistant history and real tokenizer prefix boundaries.
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"regexp"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/inference"
	"github.com/no22/RWKV-Agent/internal/tokenizer"
)

type row struct {
	Text string `json:"text"`
	Meta struct {
		ID string `json:"id"`
	} `json:"meta"`
}

func main() {
	if len(os.Args) != 4 {
		panic("usage: statealignment VOCAB NONE_JSONL FAST_JSONL")
	}
	vocab, err := tokenizer.OpenWorld(os.Args[1])
	must(err)
	pattern := regexp.MustCompile(`(?:^|\n\n)(System|User|Assistant): `)
	for fi, path := range os.Args[2:] {
		f, err := os.Open(path)
		must(err)
		scanner := bufio.NewScanner(f)
		scanner.Buffer(make([]byte, 65536), 4*1024*1024)
		mode := inference.ThinkingOff
		if fi == 1 {
			mode = inference.ThinkingFast
		}
		renderer := agent.RWKVChatRenderer{ThinkingMode: mode, HistoryThinkFast: fi == 1}
		legacy := agent.RWKVChatRenderer{ThinkingMode: mode}
		counts := map[string]int{}
		examples := []string{}
		for scanner.Scan() {
			var r row
			must(json.Unmarshal(scanner.Bytes(), &r))
			counts["rows"]++
			matches := pattern.FindAllStringSubmatchIndex(r.Text, -1)
			messages := []agent.Message{}
			fullTokens := vocab.Encode(r.Text)
			for i, m := range matches {
				label := r.Text[m[2]:m[3]]
				start := m[1]
				end := len(r.Text)
				if i+1 < len(matches) {
					end = matches[i+1][0]
				}
				content := r.Text[start:end]
				role := agent.MessageRole(strings.ToLower(label))
				if role == agent.RoleAssistant {
					expectedEnd := start - 1 // none holds back the role-space, allowing merged tokens.
					if fi == 1 {
						expectedEnd = start + len(inference.ThinkBlockFast)
					}
					expected := r.Text[:expectedEnd]
					got, err := renderer.Render(messages)
					must(err)
					old, err := legacy.Render(messages)
					must(err)
					counts["generation_prefixes"]++
					if got != expected {
						counts["aligned_byte_mismatch"]++
						if len(examples) < 5 {
							examples = append(examples, r.Meta.ID)
						}
					}
					if old != expected {
						counts["legacy_byte_mismatch"]++
					}
					tokens := vocab.Encode(got)
					equal := len(tokens) <= len(fullTokens)
					if equal {
						for j, t := range tokens {
							if fullTokens[j] != t {
								equal = false
								break
							}
						}
					}
					if !equal {
						counts["aligned_token_prefix_mismatch"]++
					}
					// Model history stores canonical action/content, so reconstruct the
					// exact empty think prefix at render time, not in the source fixture.
					if fi == 1 {
						content = strings.TrimPrefix(content, inference.ThinkBlockClosed)
					}
				}
				messages = append(messages, agent.Message{Role: role, Content: content})
			}
		}
		must(scanner.Err())
		must(f.Close())
		out, err := json.Marshal(map[string]any{"path": path, "counts": counts, "mismatch_examples": examples, "vocab_sha256": vocab.SHA256()})
		must(err)
		fmt.Println(string(out))
	}
}
func must(err error) {
	if err != nil {
		panic(err)
	}
}
