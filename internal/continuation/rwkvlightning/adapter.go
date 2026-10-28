package rwkvlightning

import (
	"bytes"
	"context"
	"crypto/tls"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

// ErrAdaptersUnsupported reports a deployment without the /v1/adapters route
// (a build older than MiSS inference). Such a server also ignores adapter_id
// in generation requests, silently running the base model.
var ErrAdaptersUnsupported = errors.New("rwkv_lightning deployment has no /v1/adapters route")

// MaxAdapterUploadBytes is the largest adapter upload the client attempts.
// Cloudflare rejects request bodies over 100 MB with HTTP 413, so a larger
// file fails fast with an explanation instead of after a long transfer.
const MaxAdapterUploadBytes = 100 << 20

// uploadHTTPClient returns the client used for multipart adapter uploads. A
// large streamed body sent over HTTP/2 through Cloudflare fails with
// "stream error: PROTOCOL_ERROR", while HTTP/1.1 succeeds, so uploads never
// negotiate h2. A caller-supplied client whose transport is not an
// *http.Transport is used as is.
func (c *Client) uploadHTTPClient() *http.Client {
	var base *http.Transport
	switch transport := c.httpClient.Transport.(type) {
	case nil:
		base, _ = http.DefaultTransport.(*http.Transport)
	case *http.Transport:
		base = transport
	}
	if base == nil {
		return c.httpClient
	}
	clone := base.Clone()
	clone.ForceAttemptHTTP2 = false
	clone.TLSNextProto = map[string]func(string, *tls.Conn) http.RoundTripper{}
	clone.TLSClientConfig = clone.TLSClientConfig.Clone()
	if clone.TLSClientConfig == nil {
		clone.TLSClientConfig = &tls.Config{}
	}
	clone.TLSClientConfig.NextProtos = []string{"http/1.1"}
	client := *c.httpClient
	client.Transport = clone
	return &client
}

// AdapterInfo describes one registered version of a MiSS adapter. The server
// keeps registrations in process RAM, so a restart forgets all of them.
type AdapterInfo struct {
	ID string `json:"id"`
	// Version is the SHA-256 of the adapter content; the most recently
	// registered version of an ID is the one generations bind by default.
	Version  string          `json:"version"`
	Manifest AdapterManifest `json:"manifest"`
}

// AdapterManifest is the subset of the package manifest clients display.
type AdapterManifest struct {
	Rank            int     `json:"rank"`
	Alpha           float64 `json:"alpha"`
	Scale           float64 `json:"scale"`
	BaseFingerprint string  `json:"base_fingerprint"`
	DType           string  `json:"dtype"`
}

type adapterListBody struct {
	Data []AdapterInfo `json:"data"`
}

type adapterRegisterBody struct {
	AdapterID string `json:"adapter_id"`
	Version   string `json:"version"`
}

// ListAdapters returns every registered adapter version.
func (c *Client) ListAdapters(ctx context.Context) ([]AdapterInfo, error) {
	request, err := c.newRequest(ctx, http.MethodGet, c.stateEndpoint("/adapters"), nil)
	if err != nil {
		return nil, err
	}
	var listed adapterListBody
	if err := c.doAdapterRequest(request, "list adapters", &listed); err != nil {
		return nil, err
	}
	return listed.Data, nil
}

// RegisterAdapterPath registers a MiSS package that already sits on the
// inference host (adapter-final.pth or a checkpoint's training.pth). path is
// resolved by the server, not locally. It returns the content version.
func (c *Client) RegisterAdapterPath(ctx context.Context, adapterID, path string) (string, error) {
	adapterID, path = strings.TrimSpace(adapterID), strings.TrimSpace(path)
	if adapterID == "" || path == "" {
		return "", fmt.Errorf("%w: adapter_id and path are required", continuation.ErrInvalidRequest)
	}
	encoded, err := json.Marshal(struct {
		AdapterID string `json:"adapter_id"`
		Path      string `json:"path"`
	}{adapterID, path})
	if err != nil {
		return "", fmt.Errorf("%w: encode adapter request: %v", ErrRemote, err)
	}
	request, err := c.newRequest(ctx, http.MethodPost, c.stateEndpoint("/adapters"), bytes.NewReader(encoded))
	if err != nil {
		return "", err
	}
	request.Header.Set("Content-Type", "application/json")
	return c.registerAdapter(request, c.httpClient)
}

// UploadAdapter uploads a local MiSS package and registers it under
// adapterID. The file is streamed, so multi-hundred-MB training checkpoints
// are not buffered in memory.
func (c *Client) UploadAdapter(ctx context.Context, adapterID, path string, progress UploadProgress) (string, error) {
	adapterID = strings.TrimSpace(adapterID)
	if adapterID == "" {
		return "", fmt.Errorf("%w: adapter_id is required", continuation.ErrInvalidRequest)
	}
	file, err := os.Open(path)
	if err != nil {
		return "", fmt.Errorf("%w: open adapter file: %v", ErrRemote, err)
	}
	defer file.Close()
	info, err := file.Stat()
	if err != nil {
		return "", fmt.Errorf("%w: stat adapter file: %v", ErrRemote, err)
	}
	if info.Size() > MaxAdapterUploadBytes {
		return "", fmt.Errorf(
			"%w: adapter file is %d MB, over the %d MB request limit of Cloudflare-fronted endpoints (HTTP 413); upload the adapter package, not the full training checkpoint",
			continuation.ErrInvalidRequest, info.Size()>>20, MaxAdapterUploadBytes>>20,
		)
	}

	// Render the form envelope (everything before and after the file bytes)
	// up front so the body length is known and the file itself streams.
	var head bytes.Buffer
	writer := multipart.NewWriter(&head)
	if err := writer.WriteField("adapter_id", adapterID); err != nil {
		return "", fmt.Errorf("%w: build multipart form: %v", ErrRemote, err)
	}
	if _, err := writer.CreateFormFile("file", filepath.Base(path)); err != nil {
		return "", fmt.Errorf("%w: build multipart form: %v", ErrRemote, err)
	}
	headBytes := append([]byte(nil), head.Bytes()...)
	head.Reset()
	if err := writer.Close(); err != nil {
		return "", fmt.Errorf("%w: close multipart form: %v", ErrRemote, err)
	}
	tail := head.Bytes()

	total := int64(len(headBytes)) + info.Size() + int64(len(tail))
	var reader io.Reader = io.MultiReader(bytes.NewReader(headBytes), file, bytes.NewReader(tail))
	if progress != nil {
		reader = &progressReader{reader: reader, total: total, report: progress}
	}
	request, err := c.newRequest(ctx, http.MethodPost, c.stateEndpoint("/adapters"), reader)
	if err != nil {
		return "", err
	}
	request.ContentLength = total
	request.Header.Set("Content-Type", writer.FormDataContentType())
	return c.registerAdapter(request, c.uploadHTTPClient())
}

// DeleteAdapter removes every version of adapterID, or only version when it
// is non-empty. Deleting an unknown ID or version succeeds.
func (c *Client) DeleteAdapter(ctx context.Context, adapterID, version string) error {
	adapterID = strings.TrimSpace(adapterID)
	if adapterID == "" {
		return fmt.Errorf("%w: adapter_id is required", continuation.ErrInvalidRequest)
	}
	encoded, err := json.Marshal(struct {
		AdapterID string `json:"adapter_id"`
		Version   string `json:"adapter_version,omitempty"`
	}{adapterID, strings.TrimSpace(version)})
	if err != nil {
		return fmt.Errorf("%w: encode adapter request: %v", ErrRemote, err)
	}
	request, err := c.newRequest(ctx, http.MethodDelete, c.stateEndpoint("/adapters"), bytes.NewReader(encoded))
	if err != nil {
		return err
	}
	request.Header.Set("Content-Type", "application/json")
	var ignored map[string]any
	return c.doAdapterRequest(request, "delete adapter", &ignored)
}

func (c *Client) registerAdapter(request *http.Request, httpClient *http.Client) (string, error) {
	var registered adapterRegisterBody
	if err := c.doAdapterRequestWith(httpClient, request, "register adapter", &registered); err != nil {
		return "", err
	}
	if strings.TrimSpace(registered.Version) == "" {
		return "", fmt.Errorf("%w: register response has no version", ErrRemote)
	}
	return registered.Version, nil
}

func (c *Client) doAdapterRequest(request *http.Request, action string, target any) error {
	return c.doAdapterRequestWith(c.httpClient, request, action, target)
}

func (c *Client) doAdapterRequestWith(httpClient *http.Client, request *http.Request, action string, target any) error {
	response, err := httpClient.Do(request)
	if err != nil {
		if ctx := request.Context(); ctx.Err() != nil {
			return ctx.Err()
		}
		return fmt.Errorf("%w: %s: %v", ErrRemote, action, err)
	}
	defer response.Body.Close()
	if response.StatusCode == http.StatusNotFound || response.StatusCode == http.StatusMethodNotAllowed {
		return fmt.Errorf("%w (HTTP %d)", ErrAdaptersUnsupported, response.StatusCode)
	}
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		return c.responseError(response)
	}
	return decodeStateBody(response.Body, target, c.password)
}
