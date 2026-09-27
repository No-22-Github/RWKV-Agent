package bench

import "testing"

func sumOf(m map[string]int) int {
	sum := 0
	for _, n := range m {
		sum += n
	}
	return sum
}

func TestScaledParallelism(t *testing.T) {
	names := []string{"workbank", "bfcl-product"}

	t.Run("default budget keeps specs", func(t *testing.T) {
		got := scaledParallelism(names, 64)
		if got["workbank"] != 48 || got["bfcl-product"] != 16 {
			t.Fatalf("specs changed at default budget: %v", got)
		}
	})

	t.Run("below specs keeps specs", func(t *testing.T) {
		got := scaledParallelism(names, 32)
		if got["workbank"] != 48 || got["bfcl-product"] != 16 {
			t.Fatalf("specs changed below budget: %v", got)
		}
	})

	t.Run("above specs fills budget", func(t *testing.T) {
		got := scaledParallelism(names, 96)
		if got["workbank"] != 72 || got["bfcl-product"] != 24 {
			t.Fatalf("want 72/24, got %v", got)
		}
		if sum := sumOf(got); sum != 96 {
			t.Fatalf("sum %d != budget 96", sum)
		}
	})

	t.Run("remainder budget keeps spec floors", func(t *testing.T) {
		got := scaledParallelism(names, 65)
		for name, spec := range map[string]int{"workbank": 48, "bfcl-product": 16} {
			if got[name] < spec {
				t.Fatalf("%s got %d < spec floor %d", name, got[name], spec)
			}
		}
		if sum := sumOf(got); sum != 65 {
			t.Fatalf("sum %d != budget 65", sum)
		}
	})

	t.Run("single suite takes full budget", func(t *testing.T) {
		got := scaledParallelism([]string{"workbank"}, 120)
		if got["workbank"] != 120 {
			t.Fatalf("want 120, got %v", got)
		}
	})
}
