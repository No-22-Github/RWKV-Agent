//go:build !chatcompletions

package chatcompletions

import (
	"context"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

type Client struct{}

func New(config Config) (*Client, error) {
	if _, err := normalizeConfig(config); err != nil {
		return nil, err
	}
	return nil, ErrNotBuilt
}

func (*Client) Continue(
	context.Context,
	continuation.Request,
	continuation.EventSink,
) (continuation.Result, error) {
	return continuation.Result{}, ErrNotBuilt
}

func (*Client) Complete(
	context.Context,
	toolchat.Request,
	continuation.EventSink,
) (toolchat.Result, error) {
	return toolchat.Result{}, ErrNotBuilt
}

func (*Client) NativeToolCalling() bool {
	return false
}

var _ continuation.Generator = (*Client)(nil)
var _ toolchat.Completer = (*Client)(nil)
