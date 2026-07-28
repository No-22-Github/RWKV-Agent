package inference

import (
	"errors"
	"fmt"
)

var (
	ErrInvalidArgument = errors.New("invalid inference argument")
	ErrUnavailable     = errors.New("inference backend unavailable")
	ErrUnsupported     = errors.New("inference operation unsupported")
	ErrBusy            = errors.New("inference session busy")
	ErrClosed          = errors.New("inference resource closed")
)

type ErrorCode string

const (
	CodeInvalidArgument ErrorCode = "invalid_argument"
	CodeUnavailable     ErrorCode = "unavailable"
	CodeUnsupported     ErrorCode = "unsupported"
	CodeBusy            ErrorCode = "busy"
	CodeCancelled       ErrorCode = "cancelled"
	CodeBackendFailure  ErrorCode = "backend_failure"
	CodeClosed          ErrorCode = "closed"
)

type Error struct {
	Op         string
	Code       ErrorCode
	Backend    BackendID
	NativeCode int
	Retryable  bool
	Err        error
}

func (e *Error) Error() string {
	if e == nil {
		return "<nil>"
	}
	prefix := e.Op
	if e.Backend != "" {
		if prefix != "" {
			prefix += " "
		}
		prefix += "[" + string(e.Backend) + "]"
	}
	if prefix == "" {
		return e.Err.Error()
	}
	return fmt.Sprintf("%s: %v", prefix, e.Err)
}

func (e *Error) Unwrap() error {
	if e == nil {
		return nil
	}
	return e.Err
}

func opError(op string, code ErrorCode, backend BackendID, err error) error {
	return &Error{Op: op, Code: code, Backend: backend, Err: err}
}
