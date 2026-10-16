package main

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync"
)

// browserUploadPath receives a file the browser picked (server mode has no
// native file dialog). The body is the raw file; the name travels in the
// query. The response is a token the frontend hands to UploadBrowserState or
// UploadBrowserAdapter, which forward the staged file to the deployment.
const browserUploadPath = "/app/upload"

// maxBrowserUpload matches the deployment's state upload limit (512 MiB);
// MiSS packages are far smaller.
const maxBrowserUpload = 512 << 20

// browserUploads stages files the browser sent until a binding forwards them.
// Each file lives in its own temporary directory under its original name, so
// the deployment sees the same filename (state IDs derive from it).
type browserUploads struct {
	mu     sync.Mutex
	staged map[string]string
}

func newBrowserUploads() *browserUploads {
	return &browserUploads{staged: map[string]string{}}
}

// middleware serves browserUploadPath and passes every other request on.
func (b *browserUploads) middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.URL.Path != browserUploadPath {
			next.ServeHTTP(writer, request)
			return
		}
		if request.Method != http.MethodPost {
			http.Error(writer, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		token, err := b.stage(request.URL.Query().Get("name"), http.MaxBytesReader(writer, request.Body, maxBrowserUpload))
		if err != nil {
			http.Error(writer, err.Error(), http.StatusBadRequest)
			return
		}
		writer.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(writer).Encode(map[string]string{"token": token})
	})
}

func (b *browserUploads) stage(name string, body io.Reader) (string, error) {
	name = filepath.Base(strings.TrimSpace(strings.ReplaceAll(name, `\`, "/")))
	if name == "" || name == "." || name == "/" {
		return "", errors.New("missing file name")
	}
	raw := make([]byte, 16)
	if _, err := rand.Read(raw); err != nil {
		return "", err
	}
	token := hex.EncodeToString(raw)
	dir, err := os.MkdirTemp("", "rwkv-agent-upload-")
	if err != nil {
		return "", err
	}
	path := filepath.Join(dir, name)
	file, err := os.Create(path)
	if err != nil {
		_ = os.RemoveAll(dir)
		return "", err
	}
	_, copyErr := io.Copy(file, body)
	closeErr := file.Close()
	if err := errors.Join(copyErr, closeErr); err != nil {
		_ = os.RemoveAll(dir)
		return "", fmt.Errorf("receive file: %w", err)
	}
	b.mu.Lock()
	b.staged[token] = path
	b.mu.Unlock()
	return token, nil
}

// take hands out a staged file once; release deletes it afterwards.
func (b *browserUploads) take(token string) (string, error) {
	b.mu.Lock()
	defer b.mu.Unlock()
	path, ok := b.staged[strings.TrimSpace(token)]
	if !ok {
		return "", errors.New("上传的文件已失效，请重新选择")
	}
	delete(b.staged, strings.TrimSpace(token))
	return path, nil
}

func (b *browserUploads) release(path string) {
	_ = os.RemoveAll(filepath.Dir(path))
}

// clear deletes every staged file that was never forwarded.
func (b *browserUploads) clear() {
	b.mu.Lock()
	defer b.mu.Unlock()
	for token, path := range b.staged {
		b.release(path)
		delete(b.staged, token)
	}
}
