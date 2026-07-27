//go:build cgo && converter

package converter

/*
#cgo CXXFLAGS: -std=c++17 -O3 -I${SRCDIR}/../../../third_party/rwkv-mobile/src
#include <stdlib.h>
#include "converter.h"
*/
import "C"

import (
	"fmt"
	"unsafe"
)

func platformAvailable() bool {
	return true
}

func platformConvert(options Options) error {
	input := C.CString(options.InputPath)
	output := C.CString(options.OutputPath)
	tokenizer := C.CString(options.TokenizerPath)
	precision := C.CString(options.Precision)
	defer C.free(unsafe.Pointer(input))
	defer C.free(unsafe.Pointer(output))
	defer C.free(unsafe.Pointer(tokenizer))
	defer C.free(unsafe.Pointer(precision))

	const errorCapacity = 8192
	errorBuffer := (*C.char)(C.malloc(errorCapacity))
	if errorBuffer == nil {
		return fmt.Errorf("allocate native converter error buffer")
	}
	defer C.free(unsafe.Pointer(errorBuffer))

	overwrite := C.int(0)
	if options.Overwrite {
		overwrite = 1
	}
	result := C.rwkv_agent_convert_pth(
		input,
		output,
		tokenizer,
		precision,
		overwrite,
		errorBuffer,
		errorCapacity,
	)
	if result != 0 {
		message := C.GoString(errorBuffer)
		if message == "" {
			message = fmt.Sprintf("native converter failed with code %d", int(result))
		}
		return fmt.Errorf("%s", message)
	}
	return nil
}
