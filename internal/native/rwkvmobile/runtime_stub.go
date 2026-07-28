//go:build !darwin || !arm64 || !cgo || !mlx

package rwkvmobile

func platformAvailable() bool { return false }

func platformOpen(Options) (runtimeImpl, error) {
	return nil, ErrUnavailable
}
