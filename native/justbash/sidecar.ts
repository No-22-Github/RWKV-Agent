// A session owns one copy-on-write workspace. No operation writes host files.
import { Bash, getCommandNames, OverlayFs } from "just-bash";
import { posix } from "node:path";
import { AsyncLocalStorage } from "node:async_hooks";
// Evaluations pin "now" (init's now_ms) so `date`, `date -d yesterday` and new
// files' mtimes agree with the datetime tool's fixed clock. The offset is
// scoped to the session's own operations through AsyncLocalStorage, so App
// sessions (no now_ms) and concurrent sessions keep their own time. Commands
// run in worker threads (js-exec, if ever enabled) do not see the offset.
const clockOffset = new AsyncLocalStorage<number>();
const RealDate = Date;
const realNow = RealDate.now.bind(RealDate);
const sessionNow = () => realNow() + (clockOffset.getStore() ?? 0);
(globalThis as any).Date = new Proxy(RealDate, {
  construct(target, args, newTarget) { return Reflect.construct(target, args.length ? args : [sessionNow()], newTarget); },
  apply(target) { return new target(sessionNow()).toString(); },
  get(target, prop, receiver) { return prop === "now" ? sessionNow : Reflect.get(target, prop, receiver); },
});
const mountPoint = "/workspace";
const commands = getCommandNames().filter((name) => name !== "sqlite3");
type Snapshot = { kind: "file" | "directory" | "missing"; data?: string; mode?: number };
type Change = { path: string; before: Snapshot; after: Snapshot };
type Request = { id: number; root: string; session?: string; op?: string; now_ms?: number; path?: string; data?: string; paths?: string[]; command?: string; timeout_ms?: number; close?: boolean; mode?: number };
class Workspace {
  overlay: OverlayFs;
  shell: Bash;
  baseline = new Map<string, Snapshot>();
  baselineBytes = 0;
  revision = 0;
  offset?: number; // ms added to the real clock for this session; unset = real time
  constructor(readonly root: string) { this.initialize(); }
  initialize() {
    this.overlay = new OverlayFs({ root: this.root, mountPoint, maxMemoryBytes: 16 * 1024 * 1024 });
    // Observe primitive mutations, including those called by cp/mv/append/link.
    for (const name of ["writeFile", "mkdir", "rm", "chmod", "utimes", "createExclusive", "symlink", "link", "cp", "mv", "appendFile"]) {
      const original = (this.overlay as any)[name].bind(this.overlay);
      (this.overlay as any)[name] = async (...args: any[]) => {
        const paths = name === "mv" ? [args[0], args[1]] : name === "cp" || name === "link" ? [args[1]] : name === "symlink" ? [args[1]] : [args[0]];
        if ((name === "rm" || name === "mv") && posix.normalize(args[0]) === mountPoint) throw new Error("cannot remove or move workspace root");
        const recursive = name === "rm" || name === "mv" || name === "cp";
        // OverlayFs would happily create entries below a file; a real filesystem refuses.
        for (const path of paths) await this.requireDirectoryParents(path);
        for (const path of paths) await this.remember(path, recursive);
        const result = await original(...args);
        if (name === "mv" || name === "cp") for (const path of paths) await this.remember(path, true);
        if (paths.some(path => path === mountPoint || path.startsWith(mountPoint + "/"))) this.revision++;
        return result;
      };
    }
    const fs = this.overlay;
    this.shell = new Bash({ fs, cwd: mountPoint, env: { HOME: mountPoint, TZ: "Asia/Shanghai" }, commands, defenseInDepth: false });
  }
  async requireDirectoryParents(path: string) {
    path = posix.normalize(path);
    for (let parent = posix.dirname(path); parent !== mountPoint && parent.startsWith(mountPoint + "/"); parent = posix.dirname(parent)) {
      if ((await this.overlay.exists(parent)) && !(await this.overlay.lstat(parent)).isDirectory) {
        const error: any = new Error(`ENOTDIR: not a directory, '${path}'`);
        error.code = "ENOTDIR";
        throw error;
      }
    }
  }
  path(path = ".") {
    const result = posix.resolve(mountPoint, path);
    if (result !== mountPoint && !result.startsWith(mountPoint + "/")) throw new Error("path escapes workspace");
    return result;
  }
  async snapshot(fs: OverlayFs, path: string): Promise<Snapshot> {
    if (!(await fs.exists(path))) return { kind: "missing" };
    const stat = await fs.lstat(path);
    if (stat.isSymbolicLink) throw new Error("symlinks are not supported in staged workspaces");
    if (stat.isDirectory) return { kind: "directory", mode: stat.mode & 0o777 };
    if (!stat.isFile) throw new Error("unsupported workspace entry");
    return { kind: "file", data: Buffer.from(await fs.readFileBuffer(path)).toString("base64"), mode: stat.mode & 0o777 };
  }
  async remember(path: string, recursive = false) {
    path = posix.normalize(path);
    if (path !== mountPoint && !path.startsWith(mountPoint + "/")) return;
    const disk = new OverlayFs({ root: this.root, mountPoint, readOnly: true });
    const capture = async (p: string) => {
      if (p === mountPoint) return;
      if (!this.baseline.has(p)) {
        if (this.baseline.size >= 10000) throw new Error("staged path limit exceeded; review existing changes first");
        const value = await this.snapshot(disk, p);
        const size = value.data?.length || 0;
        if (this.baselineBytes + size > 24 * 1024 * 1024) throw new Error("staged change baseline limit exceeded; review existing changes first");
        this.baseline.set(p, value); this.baselineBytes += size;
      }
      if (recursive && (await this.overlay.exists(p)) && (await this.overlay.lstat(p)).isDirectory)
        for (const child of await this.overlay.readdir(p)) await capture(posix.join(p, child));
    };
    await capture(path);
    for (let parent = posix.dirname(path); parent !== mountPoint && parent.startsWith(mountPoint + "/"); parent = posix.dirname(parent)) {
      if (!this.baseline.has(parent)) this.baseline.set(parent, await this.snapshot(disk, parent));
    }
  }
  async changes(): Promise<Change[]> {
    const result: Change[] = [];
    for (const [path, before] of this.baseline) {
      const after = await this.snapshot(this.overlay, path);
      if (JSON.stringify(before) !== JSON.stringify(after)) result.push({ path: posix.relative(mountPoint, path), before, after });
    }
    return result.sort((a, b) => a.path.localeCompare(b.path));
  }
  async forget(paths: string[]): Promise<Workspace> {
    const remaining = (await this.changes()).filter(c => !paths.includes(c.path));
    // Build the replacement separately. A replay failure leaves the original
    // overlay intact, including every unresolved file's original baseline.
    const replacement = new Workspace(this.root);
    replacement.offset = this.offset;
    for (const c of remaining.filter(c => c.after.kind === "missing").sort((a,b) => b.path.length-a.path.length))
      await replacement.overlay.rm(replacement.path(c.path), { recursive: true, force: true });
    for (const c of remaining.filter(c => c.after.kind !== "missing").sort((a,b) => a.path.length-b.path.length)) {
      const path = replacement.path(c.path);
      if (c.after.kind === "directory") await replacement.overlay.mkdir(path, { recursive: true });
      else { await replacement.overlay.mkdir(posix.dirname(path), { recursive: true }); await replacement.overlay.writeFile(path, Buffer.from(c.after.data!, "base64")); }
      if (c.after.mode !== undefined) await replacement.overlay.chmod(path, c.after.mode);
    }
    replacement.baseline = new Map(remaining.map(c => [replacement.path(c.path), c.before]));
    replacement.baselineBytes = remaining.reduce((sum, c) => sum + (c.before.data?.length || 0), 0);
    replacement.revision = this.revision + 1;
    return replacement;
  }
}
const workspaces = new Map<string, Workspace>();
const queues = new Map<string, Promise<void>>();
function reply(payload: object) { process.stdout.write(JSON.stringify(payload) + "\n"); }
async function handle(r: Request) {
  const key = r.session || r.root;
  try {
    if (!r.root?.startsWith("/")) throw new Error("root must be absolute");
    if (r.close) { workspaces.delete(key); reply({ id: r.id }); return; }
    let w = workspaces.get(key);
    if (r.op === "init") {
      if (!w) { w = new Workspace(r.root); workspaces.set(key, w); }
      if (typeof r.now_ms === "number") w.offset = r.now_ms - realNow();
    }
    else if (!w && r.session) throw new Error("staged session lost; restart the app (pending changes were not written to disk)");
    else if (!w) { w = new Workspace(r.root); workspaces.set(key, w); }
    if (w!.root !== r.root) throw new Error("session workspace mismatch");
    const session = w!;
    const result = session.offset === undefined ? await operate(session, r, key) : await clockOffset.run(session.offset, () => operate(session, r, key));
    reply({ id: r.id, ...result, revision: workspaces.get(key)!.revision });
  } catch (error) { reply({ id: r.id, error: String((error as Error)?.message ?? error) }); }
}
async function operate(w: Workspace, r: Request, key: string): Promise<any> {
  const path = w.path(r.path);
  let result: any = {};
  switch (r.op) {
    case "init": break;
    case "read": result.data = Buffer.from(await w.overlay.readFileBuffer(path)).toString("base64"); break;
    case "stat": { const s = await w.overlay.lstat(path); result.stat = { directory: s.isDirectory, symlink: s.isSymbolicLink, size: s.size, mode: s.mode, mtime: s.mtime.toISOString() }; break; }
    case "list": result.names = await w.overlay.readdir(path); break;
    case "write": await w.overlay.writeFile(path, Buffer.from(r.data!, "base64")); break;
    case "append": await w.overlay.appendFile(path, Buffer.from(r.data!, "base64")); break;
    case "mkdir": await w.overlay.mkdir(path, { recursive: true }); break;
    case "changes": result.changes = await w.changes(); break;
    case "forget": w = await w.forget(r.paths || []); workspaces.set(key, w); break;
    default: {
      if (typeof r.command !== "string") throw new Error("command required");
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), r.timeout_ms ?? 20000);
      try { const out = await w.shell.exec(r.command, { signal: controller.signal }); result = { stdout: out.stdout, stderr: out.stderr.replace(/^bash: ([^:\n]+): command not available in browser environments\.[^\n]*$/gm, "bash: $1: command not found"), exit_code: out.exitCode }; }
      finally { clearTimeout(timer); }
    }
  }
  return result;
}
let buffered = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk: string) => {
  buffered += chunk;
  let newline: number;
  while ((newline = buffered.indexOf("\n")) >= 0) {
    const line = buffered.slice(0, newline).trim(); buffered = buffered.slice(newline + 1);
    if (!line) continue;
    let r: Request;
    try { r = JSON.parse(line); } catch { reply({ id: 0, error: "malformed request" }); continue; }
    const key = r.session || r.root;
    const next = (queues.get(key) || Promise.resolve()).then(() => handle(r));
    queues.set(key, next);
    void next.finally(() => { if (queues.get(key) === next) queues.delete(key); });
  }
});
process.stdin.on("end", () => { void Promise.all(queues.values()).then(() => process.exit(0)); });
