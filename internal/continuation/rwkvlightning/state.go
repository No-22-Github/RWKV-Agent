package rwkvlightning

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/httputil"
)

// StateInfo describes one state uploaded to the rwkv_lightning deployment.
type StateInfo struct {
	StateID     string `json:"state_id"`
	Object      string `json:"object"`
	Filename    string `json:"filename"`
	SizeBytes   int64  `json:"size_bytes"`
	TensorCount int    `json:"tensor_count"`
	Created     int64  `json:"created"`
}

type stateListBody struct {
	Data []StateInfo `json:"data"`
}

// stateEndpoint derives the /v1/state/<suffix> URL from the configured
// inference endpoint, which callers may hand over in any of the documented
// normalization forms.
func (c *Client) stateEndpoint(suffix string) string {
	base := strings.TrimRight(c.endpoint, "/")
	if index := strings.LastIndex(base, "/v1/"); index >= 0 {
		// /v1/models, /v1/batch/completions, /v1/chat/completions, ...
		base = base[:index+len("/v1")]
	} else {
		switch {
		case strings.HasSuffix(base, "/batch/completions"):
			base = strings.TrimSuffix(base, "/batch/completions") + "/v1"
		case strings.HasSuffix(base, "/chat/completions"):
			base = strings.TrimSuffix(base, "/chat/completions") + "/v1"
		case strings.HasSuffix(base, "/v1"):
			// already the API base
		default:
			base += "/v1"
		}
	}
	return base + suffix
}

// UploadState uploads a serialized RWKV state (a PyTorch archive of the state
// tensors) and returns the state_id to reuse in generation requests. The
// deployment keeps the file in a process-local temporary directory; it is
// removed by DeleteState or when the server exits.
func (c *Client) UploadState(ctx context.Context, path string) (StateInfo, error) {
	file, err := os.Open(path)
	if err != nil {
		return StateInfo{}, fmt.Errorf("%w: open state file: %v", ErrRemote, err)
	}
	defer file.Close()

	var body bytes.Buffer
	writer := multipart.NewWriter(&body)
	part, err := writer.CreateFormFile("file", filepath.Base(path))
	if err != nil {
		return StateInfo{}, fmt.Errorf("%w: build multipart form: %v", ErrRemote, err)
	}
	if _, err := io.Copy(part, file); err != nil {
		return StateInfo{}, fmt.Errorf("%w: read state file: %v", ErrRemote, err)
	}
	if err := writer.Close(); err != nil {
		return StateInfo{}, fmt.Errorf("%w: close multipart form: %v", ErrRemote, err)
	}

	request, err := c.newRequest(ctx, http.MethodPost, c.stateEndpoint("/state/upload"), &body)
	if err != nil {
		return StateInfo{}, err
	}
	request.Header.Set("Content-Type", writer.FormDataContentType())
	response, err := c.httpClient.Do(request)
	if err != nil {
		if ctx.Err() != nil {
			return StateInfo{}, ctx.Err()
		}
		return StateInfo{}, fmt.Errorf("%w: upload state: %v", ErrRemote, err)
	}
	defer response.Body.Close()
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		return StateInfo{}, c.responseError(response)
	}
	var state StateInfo
	if err := decodeStateBody(response.Body, &state, c.password); err != nil {
		return StateInfo{}, err
	}
	if strings.TrimSpace(state.StateID) == "" {
		return StateInfo{}, fmt.Errorf("%w: upload response has no state_id", ErrRemote)
	}
	return state, nil
}

// ListStates returns every state currently held by the deployment.
func (c *Client) ListStates(ctx context.Context) ([]StateInfo, error) {
	request, err := c.newRequest(ctx, http.MethodGet, c.stateEndpoint("/state/list"), nil)
	if err != nil {
		return nil, err
	}
	response, err := c.httpClient.Do(request)
	if err != nil {
		if ctx.Err() != nil {
			return nil, ctx.Err()
		}
		return nil, fmt.Errorf("%w: list states: %v", ErrRemote, err)
	}
	defer response.Body.Close()
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		return nil, c.responseError(response)
	}
	var listed stateListBody
	if err := decodeStateBody(response.Body, &listed, c.password); err != nil {
		return nil, err
	}
	return listed.Data, nil
}

// DeleteState removes a previously uploaded state from the deployment.
func (c *Client) DeleteState(ctx context.Context, stateID string) error {
	stateID = strings.TrimSpace(stateID)
	if stateID == "" {
		return fmt.Errorf("%w: state_id is required", continuation.ErrInvalidRequest)
	}
	encoded, err := json.Marshal(struct {
		StateID string `json:"state_id"`
	}{StateID: stateID})
	if err != nil {
		return fmt.Errorf("%w: encode delete request: %v", ErrRemote, err)
	}
	request, err := c.newRequest(
		ctx,
		http.MethodDelete,
		c.stateEndpoint("/state/delete"),
		bytes.NewReader(encoded),
	)
	if err != nil {
		return err
	}
	request.Header.Set("Content-Type", "application/json")
	response, err := c.httpClient.Do(request)
	if err != nil {
		if ctx.Err() != nil {
			return ctx.Err()
		}
		return fmt.Errorf("%w: delete state: %v", ErrRemote, err)
	}
	defer response.Body.Close()
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		return c.responseError(response)
	}
	return nil
}

// decodeStateBody parses a state endpoint response, redacting the password from
// any decode error so a misbehaving deployment cannot echo it back.
func decodeStateBody(body io.Reader, target any, secret string) error {
	payload, err := io.ReadAll(io.LimitReader(body, maxResponseBytes+1))
	if err != nil {
		return fmt.Errorf("%w: read state response: %v", ErrRemote, err)
	}
	if len(payload) > maxResponseBytes {
		return fmt.Errorf("%w: state response exceeded %d bytes", ErrRemote, maxResponseBytes)
	}
	if err := json.Unmarshal(payload, target); err != nil {
		return fmt.Errorf(
			"%w: decode state response: %s",
			ErrRemote,
			httputil.SafeResponseMessage(payload, secret),
		)
	}
	return nil
}
