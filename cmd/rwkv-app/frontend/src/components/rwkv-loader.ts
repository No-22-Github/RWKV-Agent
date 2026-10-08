// @ts-nocheck
/*!
 * RWKVLoader — 圆角像素点阵加载动画（原样移植自 rwkv-pixel-loader.html，React 包装见 PixelLoader.tsx）
 * 用法：new RWKVLoader(containerElement, options)
 */
const global = window

// ---------- 字形 ----------
const BOLD = {
  R: ['XXXXXXX..','XXXXXXXX.','XX....XX.','XX....XX.','XXXXXXXX.','XXXXXXX..','XX...XX..','XX....XX.','XX.....XX'],
  W: ['XX.....XX','XX.....XX','XX.....XX','XX.....XX','XX.....XX','XX..X..XX','XX.XXX.XX','XXXX.XXXX','.XX...XX.'],
  K: ['XX....XX.','XX...XX..','XX..XX...','XX.XX....','XXXX.....','XX.XX....','XX..XX...','XX...XX..','XX....XX.'],
  V: ['XX.....XX','XX.....XX','XX.....XX','.XX...XX.','.XX...XX.','..XX.XX..','..XX.XX..','...XXX...','....X....']
};
// 笔画骨架（行, 列），用来给粗笔画像素排书写顺序
const BOLD_SKELETON = {
  R: [[[8,.5],[.5,.5],[.5,6.5],[4.5,6.5],[4.5,.5]], [[5.5,5],[8,7.5]]],
  W: [[[0,.5],[7,.5],[8,1.5],[7,3],[5,4],[7,5],[8,6.5],[7,7.5],[0,7.5]]],
  K: [[[0,.5],[8,.5]], [[0,6.5],[4,2.5],[8,6.5]]],
  V: [[[0,.5],[2,.5],[6.5,3],[8,4],[6.5,5],[2,7.5],[0,7.5]]]
};

function thinPaths() {
  const P = { R: [], W: [], K: [], V: [] };
  for (let r = 6; r >= 0; r--) P.R.push([r, 0]);
  for (let c = 1; c <= 4; c++) P.R.push([0, c]);
  P.R.push([1, 5], [2, 5]);
  for (let c = 4; c >= 1; c--) P.R.push([3, c]);
  P.R.push([4, 3], [5, 4], [6, 5]);

  for (let r = 0; r <= 5; r++) P.W.push([r, 0]);
  P.W.push([6, 1], [5, 2], [4, 3], [5, 4], [6, 5]);
  for (let r = 5; r >= 0; r--) P.W.push([r, 6]);

  for (let r = 0; r <= 6; r++) P.K.push([r, 1]);
  P.K.push([0, 5], [1, 4], [2, 3], [3, 2], [4, 3], [5, 4], [6, 5]);

  P.V = [[0,0],[1,0],[2,1],[3,1],[4,2],[5,2],[6,3],[5,4],[4,4],[3,5],[2,5],[1,6],[0,6]];
  return P;
}

function orderBySkeleton(bitmap, strokes, N) {
  const segs = [];
  let acc = 0;
  strokes.forEach(st => {
    for (let i = 0; i < st.length - 1; i++) {
      const a = st[i], b = st[i + 1];
      const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
      segs.push([a, b, len, acc]);
      acc += len;
    }
    acc += 1;
  });
  const px = [];
  bitmap.forEach((row, r) => [...row].forEach((ch, c) => {
    if (ch !== 'X') return;
    let best = Infinity, s = 0;
    segs.forEach(([a, b, len, off]) => {
      const dx = b[0] - a[0], dy = b[1] - a[1];
      let u = ((r - a[0]) * dx + (c - a[1]) * dy) / (len * len);
      u = Math.max(0, Math.min(1, u));
      const d = Math.hypot(a[0] + u * dx - r, a[1] + u * dy - c);
      if (d < best - 1e-6) { best = d; s = off + u * len; }
    });
    px.push([r * N + c, s]);
  }));
  px.sort((x, y) => x[1] - y[1]);
  return px.map(p => p[0]);
}

const GLYPHS = (function () {
  const thin = thinPaths();
  const g = { bold9: { N: 9, letters: {} }, thin7: { N: 7, letters: {} } };
  for (const ch of 'RWKV') {
    const bo = orderBySkeleton(BOLD[ch], BOLD_SKELETON[ch], 9);
    g.bold9.letters[ch] = { order: bo, set: new Set(bo) };
    const to = thin[ch].map(([r, c]) => r * 7 + c);
    g.thin7.letters[ch] = { order: to, set: new Set(to) };
  }
  return g;
})();

// ---------- 工具 ----------
const LEVELS = [0, .3, .6, 1];
const quantize = v => LEVELS.reduce((p, q) => Math.abs(q - v) < Math.abs(p - v) ? q : p);
// ease-in-out (sine) 的反函数：给定扫描进度位置，求到达时间比例
const easeInv = y => Math.acos(1 - 2 * Math.max(0, Math.min(1, y))) / Math.PI;
const hash = (a, b, c) => { const x = Math.sin(a * 12.9898 + b * 78.233 + c * 37.719) * 43758.5453; return x - Math.floor(x); };

function roundRect(ctx, x, y, s, r) {
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + s, y, x + s, y + s, r);
  ctx.arcTo(x + s, y + s, x, y + s, r);
  ctx.arcTo(x, y + s, x, y, r);
  ctx.arcTo(x, y, x + s, y, r);
  ctx.closePath();
}

// ---------- 组件 ----------
class RWKVLoader {
  constructor(container, options = {}) {
    if (!container) throw new Error('RWKVLoader: container is required');
    const single = options.layout === 'single';
    const glyph = GLYPHS[options.glyph] ? options.glyph : 'bold9';
    const thinScale = glyph === 'thin7' ? 9 / 7 : 1;

    this.o = Object.assign({
      layout: 'row',
      text: single ? 'R' : 'RWKV',
      animation: single ? 'comet' : 'scan',
      cell: Math.round((single ? 24 : 12) * thinScale),
      gap: 2,
      radius: 0.22,
      letterSpacing: null,
      color: null,
      baseAlpha: 0.07,
      quantize: true,
      autoplay: true
    }, options, { glyph });

    this.scanOpt  = Object.assign({ duration: single ? .68 : .9, hold: 0, overlap: single ? .6 : .45, direction: 'up' }, options.scan);
    this.cometOpt = Object.assign({ loop: single ? 1.6 : 4, tail: .3 }, options.comet);
    this.relayOpt = Object.assign({ period: single ? 2.2 : 3, stagger: .3 }, options.relay);
    this.decodeOpt = Object.assign({ once: false, onDone: null }, options.decode);

    this.g = GLYPHS[glyph];
    this.letters = [...String(this.o.text).toUpperCase()].filter(ch => this.g.letters[ch]).map(ch => this.g.letters[ch]);
    if (!this.letters.length) throw new Error('RWKVLoader: text must contain R, W, K or V');

    const N = this.g.N, L = this.letters.length;
    this.op = this.letters.map(() => new Float32Array(N * N));
    this.seq = [];
    this.letters.forEach((lt, li) => lt.order.forEach(k => this.seq.push([li, k])));

    this.container = container;
    this.canvas = document.createElement('canvas');
    this.canvas.setAttribute('role', 'img');
    this.canvas.setAttribute('aria-label', 'Loading');
    this.canvas.style.display = 'block';
    container.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');
    this._layout();

    this._raf = 0;
    this._elapsed = 0;
    this._done = false;
    this._reduced = global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (this._reduced) { this._static(); this._draw(); }
    else if (this.o.autoplay) this.start();
    else { this._compute(0); this._draw(); }
  }

  _layout() {
    const { cell, gap } = this.o, N = this.g.N, L = this.letters.length;
    this.ls = this.o.letterSpacing == null ? cell : this.o.letterSpacing;
    this.gw = N * cell + (N - 1) * gap;
    const w = L * this.gw + (L - 1) * this.ls, h = this.gw;
    const dpr = global.devicePixelRatio || 1;
    this.canvas.width = Math.round(w * dpr);
    this.canvas.height = Math.round(h * dpr);
    this.canvas.style.width = w + 'px';
    this.canvas.style.height = h + 'px';
    this.ctx?.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  start() {
    if (this._raf || this._reduced) return;
    this._t0 = performance.now() - this._elapsed * 1000;
    const loop = now => {
      this._elapsed = (now - this._t0) / 1000;
      this._compute(this._elapsed);
      this._draw();
      this._raf = requestAnimationFrame(loop);
    };
    this._raf = requestAnimationFrame(loop);
  }

  stop() {
    cancelAnimationFrame(this._raf);
    this._raf = 0;
  }

  replay() {
    this.stop();
    this._elapsed = 0;
    this._done = false;
    if (this._reduced) { this._static(); this._draw(); } else this.start();
  }

  destroy() {
    this.stop();
    this.canvas.remove();
  }

  _static() {
    this.letters.forEach((lt, li) => { this.op[li].fill(0); lt.order.forEach(k => this.op[li][k] = .85); });
  }

  _compute(t) {
    this.op.forEach(a => a.fill(0));
    switch (this.o.animation) {
      case 'comet': this._comet(t); break;
      case 'relay': this._relay(t); break;
      case 'decode': this._decode(t); break;
      default: this._scan(t);
    }
  }

  // 两道 45° 扫描线接力：亮线点亮、暗线熄灭，无缝循环
  _scan(t) {
    const N = this.g.N, L = this.letters.length, W = N + 1;
    const { duration: D, hold: H, overlap, direction } = this.scanOpt;
    const span = L * W - 1 + N - 1 + 4;
    const T = D + H + (1 - overlap) * D;
    const k = Math.floor(t / T);
    const fronts = [];
    for (let j = k - 2; j <= k; j++) fronts.push([j * T, 1], [j * T + D + H, 0]);
    const flashLit = D * .078, flashDim = D * .05;

    for (let li = 0; li < L; li++) {
      const set = this.letters[li].set, op = this.op[li];
      for (let q = 0; q < N * N; q++) {
        const r = Math.floor(q / N), c = q % N;
        const pos = c + li * W + (direction === 'down' ? r : N - 1 - r);
        const u = easeInv((pos + 2) / span);
        let best = -Infinity, on = 0;
        for (const [s0, st] of fronts) {
          const pt = s0 + D * u;
          if (pt <= t && pt > best) { best = pt; on = st; }
        }
        const age = t - best;
        if (set.has(q)) op[q] = age < flashLit ? 1 : (on ? .85 : 0);
        else op[q] = age < flashDim ? .3 : 0;
      }
    }
  }

  // 沿书写顺序跑的亮点 + 拖尾
  _comet(t) {
    const n = this.seq.length, L = this.letters.length;
    const tail = Math.max(4, Math.round(n / L * this.cometOpt.tail));
    const h = (t / this.cometOpt.loop * n) % n;
    this.seq.forEach(([li, k], i) => {
      const d = (h - i + n) % n;
      this.op[li][k] = d < tail ? Math.max(.22, 1 - d * (.78 / tail)) : .22;
    });
  }

  // 亮度沿笔画顺序流过，字母间依次错开
  _relay(t) {
    const { period: P, stagger } = this.relayOpt, L = this.letters.length;
    for (let li = 0; li < L; li++) {
      const order = this.letters[li].order, n = order.length;
      const offset = L > 1 ? li * stagger : 0;
      order.forEach((k, i) => {
        const u = ((((t - offset - i / n * .35) % P) + P) % P) / P;
        const pulse = u < .5 ? Math.pow(Math.sin(Math.PI * u / .5), 2) : 0;
        this.op[li][k] = .2 + .8 * pulse;
      });
    }
  }

  // 噪点乱闪，从左到右逐字解析
  _decode(t) {
    const N = this.g.N, L = this.letters.length;
    const step = L > 1 ? .45 : 0, first = L > 1 ? .5 : 1.1;
    const lastResolve = first + step * (L - 1);
    const T = lastResolve + 1.7;

    if (this.decodeOpt.once && t >= lastResolve + .2) {
      this._static();
      if (!this._done) {
        this._done = true;
        this.stop();
        this._draw();
        if (typeof this.decodeOpt.onDone === 'function') this.decodeOpt.onDone();
      }
      return;
    }

    const tt = this.decodeOpt.once ? t : t % T;
    const frame = Math.floor(t * 15);
    for (let li = 0; li < L; li++) {
      const resolveAt = first + li * step, set = this.letters[li].set, op = this.op[li];
      for (let q = 0; q < N * N; q++) {
        const lit = set.has(q);
        let v;
        if (tt < resolveAt) v = hash(q, li, frame) < (lit ? .42 : .22) ? .6 : 0;
        else { const d = tt - resolveAt; v = lit ? (d < .12 ? 1 : .85) : (d < .06 ? .3 : 0); }
        if (!this.decodeOpt.once && tt > T - .3) v *= Math.max(0, (T - tt) / .3);
        op[q] = v;
      }
    }
  }

  _draw() {
    if (!this.ctx) return; // 无 Canvas 的环境（测试用的 jsdom）只占位不绘制
    const ctx = this.ctx, N = this.g.N, { cell, gap, radius, baseAlpha } = this.o;
    const color = this.o.color || getComputedStyle(this.container).color;
    const rad = Math.min(cell / 2, cell * radius), stepPx = cell + gap;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.fillStyle = color;

    // 底层：所有像素的暗底
    ctx.globalAlpha = baseAlpha;
    ctx.beginPath();
    this.letters.forEach((_, li) => {
      const ox = li * (this.gw + this.ls);
      for (let q = 0; q < N * N; q++) roundRect(ctx, ox + (q % N) * stepPx, Math.floor(q / N) * stepPx, cell, rad);
    });
    ctx.fill();

    // 亮层：按亮度分组绘制
    const groups = new Map();
    this.letters.forEach((_, li) => {
      const ox = li * (this.gw + this.ls), op = this.op[li];
      for (let q = 0; q < N * N; q++) {
        let a = op[q];
        if (this.o.quantize) a = quantize(a);
        if (a <= 0.005) continue;
        const key = Math.round(a * 100);
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push([ox + (q % N) * stepPx, Math.floor(q / N) * stepPx]);
      }
    });
    groups.forEach((cells, key) => {
      ctx.globalAlpha = key / 100;
      ctx.beginPath();
      cells.forEach(([x, y]) => roundRect(ctx, x, y, cell, rad));
      ctx.fill();
    });
    ctx.globalAlpha = 1;
  }
}

RWKVLoader.glyphs = GLYPHS
export default RWKVLoader
