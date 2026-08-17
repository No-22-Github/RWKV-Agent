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
		return nil, fmt.Errorf("locate frontend assets: run pnpm --dir cmd/rwkv-app/frontend build: %w", err)
	}
	return os.DirFS(frontendDir), nil
}
