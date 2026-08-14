//go:build !darwin

package netproxy

import (
	"net/http"
	"net/url"
)

func loadSystemProxy() (func(*http.Request) (*url.URL, error), error) {
	return nil, nil
}
