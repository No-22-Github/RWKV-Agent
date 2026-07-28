package terminal

import (
	"fmt"
	"os"
	"strings"

	"golang.org/x/term"
)

type UIMode string

const (
	UIAuto  UIMode = "auto"
	UITUI   UIMode = "tui"
	UIPlain UIMode = "plain"
)

type Capability struct {
	Interactive bool
	Width       int
	Height      int
	Reason      string
}

func ParseUIMode(value string) (UIMode, error) {
	switch UIMode(value) {
	case UIAuto, UITUI, UIPlain:
		return UIMode(value), nil
	default:
		return "", fmt.Errorf("invalid --ui %q; expected auto, tui, or plain", value)
	}
}

func Detect(input, output *os.File) Capability {
	if input == nil || output == nil {
		return Capability{Reason: "stdin and stdout are required"}
	}
	if !term.IsTerminal(int(input.Fd())) {
		return Capability{Reason: "stdin is not a terminal"}
	}
	if !term.IsTerminal(int(output.Fd())) {
		return Capability{Reason: "stdout is not a terminal"}
	}
	if reason := environmentReason(os.Getenv); reason != "" {
		return Capability{Reason: reason}
	}
	width, height, err := term.GetSize(int(output.Fd()))
	if err != nil || width <= 0 || height <= 0 {
		return Capability{Reason: "terminal size is unavailable"}
	}
	return Capability{Interactive: true, Width: width, Height: height}
}

func SelectUI(mode UIMode, capability Capability) (UIMode, error) {
	switch mode {
	case UIPlain:
		return UIPlain, nil
	case UIAuto:
		if capability.Interactive {
			return UITUI, nil
		}
		return UIPlain, nil
	case UITUI:
		if !capability.Interactive {
			return "", fmt.Errorf("TUI requested but unavailable: %s", capability.Reason)
		}
		return UITUI, nil
	default:
		return "", fmt.Errorf("invalid UI mode %q", mode)
	}
}

func SupportsStyle(file *os.File) bool {
	if file == nil || !term.IsTerminal(int(file.Fd())) {
		return false
	}
	termName := strings.TrimSpace(strings.ToLower(os.Getenv("TERM")))
	return termName != "" && termName != "dumb" && environmentReason(os.Getenv) == ""
}

func environmentReason(getenv func(string) string) string {
	termName := strings.TrimSpace(strings.ToLower(getenv("TERM")))
	if termName == "" {
		return "TERM is empty"
	}
	if termName == "dumb" {
		return "TERM=dumb"
	}
	for _, name := range []string{
		"CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILDKITE", "CIRCLECI",
		"TF_BUILD", "TEAMCITY_VERSION", "JENKINS_URL",
	} {
		if value := strings.TrimSpace(strings.ToLower(getenv(name))); value != "" && value != "0" && value != "false" {
			return name + " is set"
		}
	}
	return ""
}
