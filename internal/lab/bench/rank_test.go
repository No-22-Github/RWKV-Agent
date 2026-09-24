package bench

import "testing"

func TestSignTest(t *testing.T) {
	if got := signTest(0, 0); got != 1.0 {
		t.Errorf("signTest(0,0) = %v, want 1", got)
	}
	if got := signTest(5, 0); got >= 0.1 {
		t.Errorf("signTest(5,0) = %v, want a small p", got)
	}
	if got := signTest(2, 2); got != 1.0 {
		t.Errorf("signTest(2,2) = %v, want 1", got)
	}
}
