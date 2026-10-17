package product

import (
	"context"
	"fmt"

	"github.com/no22/RWKV-Agent/internal/agent"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
)

// ErrSearchNotConfigured and ErrFetchNotConfigured are what web_search and
// web_fetch return when the App has no API key for them. They wrap
// agent.ErrProviderUnavailable, so the Runner marks the tool unavailable for
// the turn and the model tells the user instead of retrying.
var (
	ErrSearchNotConfigured = fmt.Errorf("%w: 未配置搜索服务，请在设置里填写 Brave 或 DeepSeek 的 key 后再使用联网搜索", agent.ErrProviderUnavailable)
	ErrFetchNotConfigured  = fmt.Errorf("%w: 未配置网页抓取服务，请在设置里填写 Tavily 或 DeepSeek 的 key 后再使用网页读取", agent.ErrProviderUnavailable)
)

type missingSearch struct{}

func (missingSearch) Search(context.Context, assistanttools.WebSearchRequest) ([]assistanttools.WebSearchResult, error) {
	return nil, ErrSearchNotConfigured
}

type missingFetch struct{}

func (missingFetch) Fetch(context.Context, assistanttools.WebFetchRequest) ([]assistanttools.WebFetchResult, error) {
	return nil, ErrFetchNotConfigured
}

// MissingWebSearch is the placeholder search provider for a connection without
// a search key.
func MissingWebSearch() assistanttools.WebSearchProvider { return missingSearch{} }

// MissingWebFetch is the placeholder fetch provider for a connection without
// a fetch key.
func MissingWebFetch() assistanttools.WebFetchProvider { return missingFetch{} }
