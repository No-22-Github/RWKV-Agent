package main

import (
	"embed"
	"flag"
	"fmt"
	"io/fs"
	"log"
	"os"
	"path/filepath"

	agentapi "github.com/no22/RWKV-Agent/api"
	"github.com/wailsapp/wails/v3/pkg/application"
)

//go:embed all:frontend/dist
var embeddedFrontend embed.FS

func main() {
	options, err := parseOptions(os.Args[1:])
	if err != nil {
		log.Fatal(err)
	}
	frontend, err := fs.Sub(embeddedFrontend, "frontend/dist")
	if err != nil {
		log.Fatal(err)
	}
	service, err := agentapi.NewService(agentapi.Options{Workspace: options.workspace})
	if err != nil {
		log.Fatal(err)
	}
	backend := newAppService(service)
	app := application.New(application.Options{
		Name:        "RWKV Agent",
		Description: "Local-first RWKV workspace agent",
		Services: []application.Service{
			application.NewService(backend),
		},
		Assets: application.AssetOptions{
			Handler:        application.BundledAssetFileServer(frontend),
			DisableLogging: true,
		},
		Server: application.ServerOptions{
			Host: options.host,
			Port: options.port,
		},
		Mac: application.MacOptions{
			ApplicationShouldTerminateAfterLastWindowClosed: true,
		},
		OnShutdown: func() {
			_ = backend.Close()
		},
	})
	backend.setApplication(app)
	configureWindow(app)
	if serverBuild {
		fmt.Fprintf(os.Stderr, "RWKV Agent server: http://%s:%d\n", options.host, options.port)
	}
	if err := app.Run(); err != nil {
		log.Fatal(err)
	}
}

type launchOptions struct {
	host      string
	port      int
	workspace string
}

func parseOptions(arguments []string) (launchOptions, error) {
	var options launchOptions
	flags := flag.NewFlagSet("rwkv-app", flag.ContinueOnError)
	flags.StringVar(&options.host, "host", "127.0.0.1", "server-mode bind address")
	flags.IntVar(&options.port, "port", 8080, "server-mode HTTP port")
	flags.StringVar(&options.workspace, "workspace", ".", "workspace exposed to read-only Agent tools")
	if err := flags.Parse(arguments); err != nil {
		return launchOptions{}, err
	}
	if options.port < 1 || options.port > 65535 {
		return launchOptions{}, fmt.Errorf("port must be between 1 and 65535")
	}
	absolute, err := filepath.Abs(options.workspace)
	if err != nil {
		return launchOptions{}, err
	}
	options.workspace = absolute
	return options, nil
}
