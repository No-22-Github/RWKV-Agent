package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"os"
	"strings"
	"time"
)

// runAdapter manages MiSS adapters registered on an rwkv_lightning server.
// Registering by --path uses a package already on the inference host, which
// is how training outputs are normally served; the App only uploads local
// files.
func runAdapter(args []string) error {
	if len(args) == 0 {
		return errors.New("adapter requires a subcommand: register, list, or delete")
	}
	switch args[0] {
	case "register":
		return runAdapterRegister(args[1:])
	case "list":
		return runAdapterList(args[1:])
	case "delete":
		return runAdapterDelete(args[1:])
	default:
		return fmt.Errorf("unknown adapter subcommand %q; use register, list, or delete", args[0])
	}
}

func runAdapterRegister(args []string) error {
	var flags stateFlags
	fs := flag.NewFlagSet("adapter register", flag.ContinueOnError)
	registerStateFlags(fs, &flags)
	id := fs.String("adapter-id", "", "adapter_id to register under; registering an existing ID adds a new default version")
	path := fs.String("path", "", "MiSS PTH on the inference host (adapter-final.pth or a checkpoint's training.pth); relative paths resolve against the server's working directory")
	file := fs.String("file", "", "local MiSS PTH to upload instead of --path")
	if err := fs.Parse(args); err != nil {
		return err
	}
	if strings.TrimSpace(*id) == "" {
		return errors.New("adapter register requires --adapter-id")
	}
	if (strings.TrimSpace(*path) == "") == (strings.TrimSpace(*file) == "") {
		return errors.New("adapter register requires exactly one of --path or --file")
	}
	client, err := flags.client()
	if err != nil {
		return err
	}
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Minute)
	defer cancel()
	var version string
	if strings.TrimSpace(*path) != "" {
		version, err = client.RegisterAdapterPath(ctx, *id, *path)
	} else {
		version, err = client.UploadAdapter(ctx, *id, *file, nil)
	}
	if err != nil {
		return fmt.Errorf("register adapter: %w", err)
	}
	fmt.Fprintf(os.Stdout, "%s\t%s\n", strings.TrimSpace(*id), version)
	return nil
}

func runAdapterList(args []string) error {
	var flags stateFlags
	fs := flag.NewFlagSet("adapter list", flag.ContinueOnError)
	registerStateFlags(fs, &flags)
	if err := fs.Parse(args); err != nil {
		return err
	}
	client, err := flags.client()
	if err != nil {
		return err
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	adapters, err := client.ListAdapters(ctx)
	if err != nil {
		return fmt.Errorf("list adapters: %w", err)
	}
	fmt.Fprintln(os.Stdout, "adapter_id\tversion\trank\talpha\tbase_fingerprint")
	for _, adapter := range adapters {
		fmt.Fprintf(
			os.Stdout,
			"%s\t%s\t%d\t%g\t%s\n",
			adapter.ID,
			adapter.Version,
			adapter.Manifest.Rank,
			adapter.Manifest.Alpha,
			adapter.Manifest.BaseFingerprint,
		)
	}
	return nil
}

func runAdapterDelete(args []string) error {
	var flags stateFlags
	fs := flag.NewFlagSet("adapter delete", flag.ContinueOnError)
	registerStateFlags(fs, &flags)
	id := fs.String("adapter-id", "", "adapter_id to unregister")
	version := fs.String("version", "", "only unregister this content version; empty removes every version")
	if err := fs.Parse(args); err != nil {
		return err
	}
	if strings.TrimSpace(*id) == "" {
		return errors.New("adapter delete requires --adapter-id")
	}
	client, err := flags.client()
	if err != nil {
		return err
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	if err := client.DeleteAdapter(ctx, *id, *version); err != nil {
		return fmt.Errorf("delete adapter: %w", err)
	}
	fmt.Fprintf(os.Stdout, "deleted %s\n", strings.TrimSpace(*id))
	return nil
}
