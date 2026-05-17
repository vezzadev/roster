package main

import "testing"

func TestRun(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name     string
		args     []string
		wantExit int
	}{
		{
			name:     "no args",
			args:     []string{},
			wantExit: 0,
		},
		{
			name:     "help flag",
			args:     []string{"--help"},
			wantExit: 0,
		},
		{
			name:     "version command",
			args:     []string{"version"},
			wantExit: 0,
		},
		{
			name:     "unknown command",
			args:     []string{"notacommand"},
			wantExit: 1,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			got := run(tc.args)
			if got != tc.wantExit {
				t.Fatalf("run(%v) = %d, want %d", tc.args, got, tc.wantExit)
			}
		})
	}
}
