// Package main is the entrypoint for the CLI.
package main

import (
	"os"

	"github.com/pedropaulovc/go-project/internal/cmd"
)

var version = "dev" //nolint:gochecknoglobals,nolintlint // injected at build time via -ldflags

func main() {
	os.Exit(run(os.Args[1:]))
}

func run(args []string) int {
	root := cmd.NewRoot(version)
	root.SetArgs(args)

	if err := root.Execute(); err != nil {
		return 1
	}

	return 0
}
