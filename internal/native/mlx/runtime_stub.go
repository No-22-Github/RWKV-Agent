//go:build !darwin || !arm64 || !cgo || !mlx

package mlx

func platformAvailable() bool {
	return false
}

func platformOpen(_, _ string) (runtimeImpl, error) {
	return nil, ErrUnavailable
}
