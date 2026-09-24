package lab

// Python's random module, for the one place the migration cannot substitute an
// equivalent generator: `run compare`'s bootstrap writes its confidence
// interval into a report, and a different stream would silently invalidate
// every interval already recorded (P7).
//
// This is CPython's _randommodule.c MT19937 with the seeding path a small int
// takes: seed(0) splits the absolute value into 32-bit words ([0]) and calls
// init_by_array, not init_genrand. randrange(n) is _randbelow(n), which draws
// `n.bit_length()` bits at a time and rejects until the draw is in range.

const (
	mtN         = 624
	mtM         = 397
	mtMatrixA   = 0x9908b0df
	mtUpperMask = 0x80000000
	mtLowerMask = 0x7fffffff
)

// PyRandom is random.Random.
type PyRandom struct {
	mt  [mtN]uint32
	mti int
}

// NewPyRandom is random.Random(seed) for a non-negative seed.
func NewPyRandom(seed int64) *PyRandom {
	r := &PyRandom{}
	r.initGenrand(19650218)
	// init_by_array with the seed's 32-bit words, most significant first.
	var key []uint32
	if seed == 0 {
		key = []uint32{0}
	}
	for v := uint64(seed); v > 0; v >>= 32 {
		key = append([]uint32{uint32(v & 0xffffffff)}, key...)
	}
	r.initByArray(key)
	return r
}

func (r *PyRandom) initGenrand(s uint32) {
	r.mt[0] = s
	for i := 1; i < mtN; i++ {
		prev := r.mt[i-1]
		r.mt[i] = 1812433253*(prev^(prev>>30)) + uint32(i)
	}
	r.mti = mtN
}

func (r *PyRandom) initByArray(key []uint32) {
	r.initGenrand(19650218)
	i, j := 1, 0
	k := mtN
	if len(key) > k {
		k = len(key)
	}
	for ; k > 0; k-- {
		prev := r.mt[i-1]
		r.mt[i] = (r.mt[i] ^ ((prev ^ (prev >> 30)) * 1664525)) + key[j] + uint32(j)
		i++
		j++
		if i >= mtN {
			r.mt[0] = r.mt[mtN-1]
			i = 1
		}
		if j >= len(key) {
			j = 0
		}
	}
	for k = mtN - 1; k > 0; k-- {
		prev := r.mt[i-1]
		r.mt[i] = (r.mt[i] ^ ((prev ^ (prev >> 30)) * 1566083941)) - uint32(i)
		i++
		if i >= mtN {
			r.mt[0] = r.mt[mtN-1]
			i = 1
		}
	}
	r.mt[0] = 0x80000000
}

// Uint32 is genrand_uint32.
func (r *PyRandom) Uint32() uint32 {
	if r.mti >= mtN {
		var y uint32
		var kk int
		for kk = 0; kk < mtN-mtM; kk++ {
			y = (r.mt[kk] & mtUpperMask) | (r.mt[kk+1] & mtLowerMask)
			r.mt[kk] = r.mt[kk+mtM] ^ (y >> 1) ^ (-(y & 1) & mtMatrixA)
		}
		for ; kk < mtN-1; kk++ {
			y = (r.mt[kk] & mtUpperMask) | (r.mt[kk+1] & mtLowerMask)
			r.mt[kk] = r.mt[kk+(mtM-mtN)] ^ (y >> 1) ^ (-(y & 1) & mtMatrixA)
		}
		y = (r.mt[mtN-1] & mtUpperMask) | (r.mt[0] & mtLowerMask)
		r.mt[mtN-1] = r.mt[mtM-1] ^ (y >> 1) ^ (-(y & 1) & mtMatrixA)
		r.mti = 0
	}
	y := r.mt[r.mti]
	r.mti++
	y ^= y >> 11
	y ^= (y << 7) & 0x9d2c5680
	y ^= (y << 15) & 0xefc60000
	y ^= y >> 18
	return y
}

// GetRandBits is getrandbits(k) for 0 <= k <= 32.
func (r *PyRandom) GetRandBits(k uint) uint32 {
	if k == 0 {
		return 0
	}
	return r.Uint32() >> (32 - k)
}

// RandRange is randrange(n) for n > 0: _randbelow(n).
func (r *PyRandom) RandRange(n int) int {
	if n <= 0 {
		return 0
	}
	bits := uint(bitLength(n))
	for {
		v := r.GetRandBits(bits)
		if int(v) < n {
			return int(v)
		}
	}
}

func bitLength(n int) int {
	bits := 0
	for v := n; v > 0; v >>= 1 {
		bits++
	}
	return bits
}
