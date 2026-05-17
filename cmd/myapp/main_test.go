// Package main_test contains integration tests for the myapp CLI binary.
package main_test

import (
	"context"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
	"time"
)

type cliIntegrationCase struct {
	name     string
	arg      string
	wantExit int
}

// buildBinary compiles the binary into a temp directory and returns its path.
func buildBinary(t *testing.T) string {
	t.Helper()

	dir := t.TempDir()

	name := "myapp"

	if runtime.GOOS == "windows" {
		name += ".exe"
	}

	out := filepath.Join(dir, name)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	//nolint:gosec // test build output path is controlled by this test
	cmd := exec.CommandContext(ctx, "go", "build", "-o", out, ".")
	cmd.Dir = filepath.Join(findModuleRoot(t), "cmd", "myapp")

	if output, err := cmd.CombinedOutput(); err != nil {
		t.Fatalf("build failed: %v\n%s", err, output)
	}

	return out
}

// findModuleRoot walks up from the test file's directory to find go.mod.
func findModuleRoot(t *testing.T) string {
	t.Helper()

	dir, err := os.Getwd()
	if err != nil {
		t.Fatalf("getwd: %v", err)
	}

	for {
		if _, err := os.Stat(filepath.Join(dir, "go.mod")); err == nil {
			return dir
		}

		parent := filepath.Dir(dir)
		if parent == dir {
			t.Fatal("could not find go.mod")
		}

		dir = parent
	}
}

func TestCLIIntegration(t *testing.T) {
	t.Parallel()

	if testing.Short() {
		t.Skip("skipping CLI integration test in short mode")
	}

	bin := buildBinary(t)
	tests, wantOutByName := cliIntegrationCases()

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			var args []string
			if tc.arg != "" {
				args = append(args, tc.arg)
			}

			out, exitCode, err := runBinary(t, bin, args...)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			if exitCode != tc.wantExit {
				t.Errorf("exit code = %d, want %d\noutput: %s", exitCode, tc.wantExit, out)
			}

			if wantOut, ok := wantOutByName[tc.name]; ok && !strings.Contains(string(out), wantOut) {
				t.Errorf("output %q does not contain %q", string(out), wantOut)
			}
		})
	}
}

//nolint:gocritic // returning both cases and expectations keeps test data setup concise
func cliIntegrationCases() ([]cliIntegrationCase, map[string]string) {
	tests := []cliIntegrationCase{
		{
			name:     "no args prints help",
			wantExit: 0,
		},
		{
			name:     "help flag prints usage",
			arg:      "--help",
			wantExit: 0,
		},
		{
			name:     "version subcommand prints version",
			arg:      "version",
			wantExit: 0,
		},
		{
			name:     "unknown command exits non-zero",
			arg:      "notacommand",
			wantExit: 1,
		},
	}

	wantOutByName := map[string]string{
		"no args prints help":               "myapp",
		"help flag prints usage":            "Usage:",
		"version subcommand prints version": "dev",
	}

	return tests, wantOutByName
}

//nolint:gocritic // unnamed result avoids nonamedreturns lint in this repo configuration
func runBinary(t *testing.T, bin string, args ...string) ([]byte, int, error) {
	t.Helper()

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	//nolint:gosec // test binary path is built by this test
	cmd := exec.CommandContext(ctx, bin, args...)

	out, err := cmd.CombinedOutput()
	if err == nil {
		return out, 0, nil
	}

	var exitErr *exec.ExitError
	if errors.As(err, &exitErr) {
		return out, exitErr.ExitCode(), nil
	}

	return out, 0, fmt.Errorf("run binary: %w", err)
}
