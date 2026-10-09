// just-bash sidecar for the Go `bash` tool (internal/agent/tools/bash.go).
//
// Protocol: one JSON request per stdin line, one JSON response per stdout
// line, matched by id. Requests may overlap; each runs on the shell bound to
// its workspace root.
//
//   request  {"id":1,"root":"/abs/workspace","command":"ls","timeout_ms":20000}
//   response {"id":1,"stdout":"...","stderr":"...","exit_code":0}
//            {"id":1,"error":"..."}                      (protocol failure)
//            {"id":1,"close":true} closes the shell bound to root.
//
// Filesystem: the workspace root is mounted read-write at /workspace (the
// cwd of every command); everything else, /tmp included, is in memory, so a
// command can neither read nor write outside the workspace.
//
// Compiled with `bun build --compile` (scripts/build-justbash.sh). Under Bun
// the defense-in-depth layer must stay off: its global patching makes the
// first file access inside exec fail. The filesystem layer above is the
// isolation boundary; the layer is only a secondary guard upstream.
import { Bash, getCommandNames, InMemoryFs, MountableFs, ReadWriteFs } from "just-bash";

const mountPoint = "/workspace";

// sqlite3 needs a worker file that a single-file binary cannot ship;
// python3 / js-exec are off unless enabled explicitly in the options.
const commands = getCommandNames().filter((name) => name !== "sqlite3");

type Request = { id: number; root?: string; command?: string; timeout_ms?: number; close?: boolean };

// Shells are cached per root so /tmp survives between calls of one session;
// the oldest is dropped beyond maxShells (Map keeps insertion order).
const maxShells = 64;
const shells = new Map<string, Bash>();

function shellFor(root: string): Bash {
  let shell = shells.get(root);
  if (shell) {
    shells.delete(root);
  } else {
    const fs = new MountableFs({
      base: new InMemoryFs(),
      mounts: [{ mountPoint, filesystem: new ReadWriteFs({ root }) }],
    });
    shell = new Bash({
      fs,
      cwd: mountPoint,
      env: { HOME: mountPoint, TZ: "Asia/Shanghai" },
      commands,
      defenseInDepth: false,
    });
  }
  shells.set(root, shell);
  if (shells.size > maxShells) shells.delete(shells.keys().next().value!);
  return shell;
}

// Commands excluded above report a bundle-specific hint upstream; the model
// should see the ordinary shell message instead.
const unavailable = /^bash: ([^:\n]+): command not available in browser environments\.[^\n]*$/gm;

function reply(payload: Record<string, unknown>) {
  process.stdout.write(JSON.stringify(payload) + "\n");
}

async function handle(request: Request) {
  const { id } = request;
  if (!request.root || !request.root.startsWith("/")) {
    reply({ id, error: "root must be an absolute path" });
    return;
  }
  if (request.close) {
    shells.delete(request.root);
    reply({ id, close: true });
    return;
  }
  if (typeof request.command !== "string") {
    reply({ id, error: "command is required" });
    return;
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), request.timeout_ms ?? 20000);
  try {
    const result = await shellFor(request.root).exec(request.command, { signal: controller.signal });
    const stderr = result.stderr.replace(unavailable, "bash: $1: command not found");
    reply({ id, stdout: result.stdout, stderr, exit_code: result.exitCode });
  } catch (error) {
    reply({ id, error: String((error as Error)?.message ?? error) });
  } finally {
    clearTimeout(timer);
  }
}

let buffered = "";
let pending = 0;
let ended = false;
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk: string) => {
  buffered += chunk;
  let newline: number;
  while ((newline = buffered.indexOf("\n")) >= 0) {
    const line = buffered.slice(0, newline).trim();
    buffered = buffered.slice(newline + 1);
    if (!line) continue;
    let request: Request;
    try {
      request = JSON.parse(line);
    } catch {
      reply({ id: 0, error: "malformed request line" });
      continue;
    }
    pending++;
    void handle(request).finally(() => {
      pending--;
      if (ended && pending === 0) process.exit(0);
    });
  }
});
process.stdin.on("end", () => {
  ended = true;
  if (pending === 0) process.exit(0);
});
