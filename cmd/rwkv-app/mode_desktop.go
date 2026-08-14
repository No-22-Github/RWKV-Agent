//go:build !server

package main

import "github.com/wailsapp/wails/v3/pkg/application"

const serverBuild = false

func configureWindow(app *application.App) {
	app.Window.NewWithOptions(application.WebviewWindowOptions{
		Name:             "main",
		Title:            "RWKV Agent",
		URL:              "/",
		Width:            1440,
		Height:           900,
		MinWidth:         900,
		MinHeight:        640,
		BackgroundColour: application.NewRGB(248, 249, 251),
		Mac: application.MacWindow{
			Backdrop:                application.MacBackdropTranslucent,
			TitleBar:                application.MacTitleBarHiddenInsetUnified,
			InvisibleTitleBarHeight: 48,
		},
	})
}
