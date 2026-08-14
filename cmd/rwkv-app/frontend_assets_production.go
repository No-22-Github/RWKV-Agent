//go:build production

package main

import (
	"embed"
	"io/fs"
)

//go:embed all:frontend/dist
var embeddedFrontend embed.FS

func frontendAssets() (fs.FS, error) {
	return fs.Sub(embeddedFrontend, "frontend/dist")
}
