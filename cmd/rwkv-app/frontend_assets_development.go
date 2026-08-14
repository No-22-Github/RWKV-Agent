//go:build !production

package main

import (
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"runtime"
)

func frontendAssets() (fs.FS, error) {
	_, sourceFile, _, ok := runtime.Caller(0)
	if !ok {
		return nil, fmt.Errorf("locate frontend assets: caller information unavailable")
	}
	frontendDir := filepath.Join(filepath.Dir(sourceFile), "frontend", "dist")
	if _, err := os.Stat(filepath.Join(frontendDir, "index.html")); err != nil {
		return nil, fmt.Errorf("locate frontend assets: run npm --prefix cmd/rwkv-app/frontend run build: %w", err)
	}
	return os.DirFS(frontendDir), nil
}
