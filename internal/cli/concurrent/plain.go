package concurrent

import (
	"context"
	"fmt"
	"io"

	"github.com/no22/RWKV-Agent/internal/terminal"
)

type PlainRenderer struct {
	Out    io.Writer
	Status io.Writer
}

func (p PlainRenderer) Run(ctx context.Context, runner *Runner) (Summary, error) {
	if p.Out == nil {
		p.Out = io.Discard
	}
	if p.Status == nil {
		p.Status = io.Discard
	}
	defer runner.Close()
	summary, err := runner.Run(ctx)
	snapshot := runner.Snapshot()
	for _, session := range snapshot.Sessions {
		fmt.Fprintf(
			p.Out,
			"session %d (%d tokens): %s\n",
			session.Index,
			session.OutputTokens,
			terminal.SanitizeModelText(session.Output),
		)
	}
	fmt.Fprintln(p.Status, summary.String())
	return summary, err
}
