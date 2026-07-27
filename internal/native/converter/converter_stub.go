//go:build !cgo || !converter

package converter

func platformAvailable() bool {
	return false
}

func platformConvert(Options) error {
	return ErrUnavailable
}
