import { handleMeshApi, meshOpenApiPaths, meshPointer } from "./mesh.js";
import { LIMITATION, MODES, TARGETS, VERSION, overlayFromB64, listUnredact, UNREDACT_NOTE, unredactFromB64 } from "./overlay.js";
import { classifyRequest, readBotManagement } from "./classify.js";
import {
  isolatedKeys,
  isReservedCounterKey,
  shapeCountBody,
  shapeHumanBotFields,
} from "./stats-shape.js";
const EXAMPLE_PAYLOAD = {
  "mode": "rosetta",
  "lens": "rosetta",
  "target": "ink",
  "inject": true,
  "note": "Rosetta spectral analysis preview (256px). inject true|false is paint, not pigment recovery. Same lenses as Aziel Corpus Library OCR."
};

const SKILL_MARKDOWN = "---\nname: SpectralLock\ndescription: Use when calling SpectralLock hosted /v1 or installing the local package. Dual surface: Worker /v1 + catalog MCP. This Worker /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 hub cite / Worker mesh cross-map only (photon QNS1 packet transfer). No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Not a Softwares-tab product. Rosetta spectral analysis \u2014 same lenses as Aziel Corpus Library OCR (overlays, ink/page). Author Aziel Eliab.\n---\n\n# SpectralLock\n\nRosetta spectral analysis software (RSA-2.0 family). Same SpectralLock lenses as Aziel Corpus Library OCR: overlays plus ink/page targets. LIVE modes: `zero`, `tazel`, `vyrn`, `uv` (aliases `ultraviolet`, `uv-light`, `uvsa`), `rosetta`, `zen`, `chaos`, `balance`, `candle` (aliases `candlelight`, `candle-light`), `indent` (aliases `indentation`, `suppress-ink`, `ink-suppress`, `revealer-indent`), `lemon` (aliases `lemon-ink`, `hidden-lemon`, `invisible-ink-lemon`). Honest unredact family (not a lens): `unredact` / `lift` / `redact-locate` with ops `locate`, `lift`, `recover`, `refuse`. Locate leftover / historical page bytes and residual only \u2014 never invent letters. Opaque rewrite with nothing left refuses `SL-UNREDACT-OPAQUE`. OCR only after structural recovery. Synthetic image analysis \u2014 not a lab instrument, not forensic certification. Stub: `spectrometer`, `forensic`, `invent_mark`. Author: **Aziel Eliab**.\n\n**THIS IS:** Rosetta spectral analysis \u2014 SpectralLock lenses, overlays, and ink/page modes, aligned with [Aziel Corpus Library OCR](https://www.azielcorpuslibrary.net/ocr).\n\n**THIS IS NOT:** a court exhibit or a claim of authenticity. Hosted `/v1` does not increment downloads or views.\n\nAlways send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.\n\n## Call these URLs\n\n- Worker OpenAPI: https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json\n- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json\n- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`\n- Live skill (this markdown): `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill`\n- Suite mesh: `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/mesh` (PROXY; default OFF; QNS-CD-1.0 cross-map)\n- Corpus OCR (reference): https://www.azielcorpuslibrary.net/ocr\n\nOps (do **not** increment downloads or views):\n\n| Method | Path | What |\n|--------|------|------|\n| GET | `/v1/health` | Liveness. Does not increment downloads. |\n| GET | `/v1/skill` | This markdown. Does not increment downloads. |\n| GET | `/v1/modes` | List SpectralLock lenses (canonical ids + aliases). |\n| GET | `/v1/lenses` | Alias for `/v1/modes`. |\n| GET | `/v1/targets` | Ink and page targets. |\n| POST | `/v1/overlay` | Rosetta spectral overlay on a posted PNG (base64). Accepts `mode`/`lens`/`lenses`, `target` (`ink`\\|`page`), and `inject` (`true`\\|`false`). ON is false-color membership tint (paint), not recovered pigment. OFF is gray of the same gate. Zero ignores the switch. Returns `tazel_inband_pct` and `vyrn_inband_pct` before any hit claim. 256 px preview; prefer local `spectrallock_inject.py`. |\n| GET | `/v1/unredact` | Honesty banner + unredact ops (`locate`, `lift`, `recover`, `refuse`). Does not increment downloads. |\n| POST | `/v1/unredact` | Locate leftover / historical page bytes. Body `{b64, op, query, twin_b64?}`. Returns `leftover_bytes`, `recovered_from`, `page_revisions`, `revision_compare`, `revision_graph` (`revisions[]` with tip-cut `copy` `{media_type, filename, b64, sha256, byte_length, source_revision}` plus surviving embeds; `edges[]` with added/replaced/deleted/freed / `page_deltas` / `redaction_ops` classified `replaced` \\| `overlaid` \\| `detached` \\| `sanitized rewrite`; `root_startxref`, `eof_offsets`), `operator_text`, `classifications`, `recovered_characters` (page / object_id / generation / xref_revision / stream_offset / operator / font / decoded_bytes / source_revision / sha256), `ocr` (after structural only; never covered letters from context), `refuse_code` (`SL-UNREDACT-OPAQUE`). Hosted preview may cap copy size (sha256+offset cites; no invented bytes) and has no OCR engine \u2014 it does not lie about that. Aliases: `POST /v1/lift`, `POST /v1/redact-locate`. |\n| GET | `/v1/mesh` | PROXY suite mesh status. Default OFF. QNM live|locked|isolated. QNS-CD-1.0 cross-map (photon QNS1; not a Softwares-tab product). Never enables. No public qnsd proxy. |\n| GET | `/v1/mesh/nodes` | PROXY Live Nodes roster (5-minute presence). Peers see the QNS-CD-1.0 cross-map. |\n| POST | `/v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` | PROXY. Bearer required to enable. No auto-heal. Anon-broadcast is not a publish path. |\n\nWorks with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import OpenAPI as a custom tool, GPT Action, HTTP tool, or MCP connector. Catalog MCP `mesh_*` + FragGate `slug=mesh`. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 hub cite / Worker mesh cross-map only (photon QNS1 packet transfer; local qnsd in https://github.com/AzielEliab/qnm-node; runtime cites in https://github.com/AzielEliab/aziel-runtime). No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Not a Softwares-tab product.\n\n## Example\n\n```bash\ncurl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/health\ncurl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill\ncurl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/lenses\ncurl -s -A 'Mozilla/5.0' https://spectrallock-download-tracker.vibelock.workers.dev/v1/mesh\n```\n\n## Local (after one-click install)\n\n```bash\ncurl -fsSL https://spectrallock-download-tracker.vibelock.workers.dev/install.sh | bash\nspectrallock ui\nspectrallock doctor\n```\n\nThen open http://127.0.0.1:8861 (loopback only).\n\nCounted download (gzip HTTP 200, no 302): https://spectrallock-download-tracker.vibelock.workers.dev/download?asset=spectrallock-0.3.0.tar.gz\nGitHub: https://github.com/AzielEliab/spectrallock\n\n## Catalog + local UI\n\nAuthor: **Aziel Eliab**. Rosetta spectral analysis. 256px hosted preview; full pipeline is the Python package. Lamb Lens: Service \u2192 Clarity \u2192 Peace. Never invent marks.\n\n- Catalog product: https://aziel-runtime.vibelock.workers.dev/p/spectrallock/\n- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json\n- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`\n- This Worker skill: `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/skill`\n- This Worker OpenAPI: https://spectrallock-download-tracker.vibelock.workers.dev/openapi.json\n- Sample payload: `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/example`\n- Suite mesh: `GET https://spectrallock-download-tracker.vibelock.workers.dev/v1/mesh` PROXY (default OFF; QNS-CD-1.0 cross-map)\n\nLocal UI: **Import JSON file** (`type=file`) and **Export JSON**. Lenses + Ink/Page + inject ON/OFF. Then `spectrallock doctor`. Worker homepage Live Nodes strip polls `GET /v1/mesh` (default OFF). QNS-CD-1.0 is a hub cite / Worker mesh cross-map only \u2014 not a Softwares-tab product; no public qnsd proxy.\n\nColor inject (operator lock 19 Sep 2026): `--inject` / `--no-inject` on every named mode. ON paints membership; OFF is luminance of the same gate; `zero` stays gray. tazel=170\u00b0 `#1EC9A5`, vyrn=350\u00b0 `#C00066`. UV is synthetic, not a lamp. Balance does not invent marks. Report `tazel_inband_pct` and `vyrn_inband_pct` before claiming a hit. Empty gate \u2260 broken lens. Prefer `python3 spectrallock_inject.py`. Identity: Aziel Eliab. Lamb Lens: Service \u2192 Clarity \u2192 Peace. NO-LIE.\n\nUnredact / lift-overlay (operator lock 2026-09-19 \u2014 NO-LIE): `locate` reports text still in the PDF, metadata, attachments, twin-page residual, leftover container bytes, and historical page revisions (stale `/Page` graphs, prior streams, xref/ObjStm, after-EOF, incremental `startxref`/`Prev` revision graph + per-revision tip-cut PDF/embed copies). That is reading bytes that are still present \u2014 not guessing a black box. `lift` is non-opaque residual with `--no-inject` only; heatmaps are not transcripts. Opaque sanitized rewrite with nothing left refuses `SL-UNREDACT-OPAQUE`. If leftover / historical bytes remain, `recover` surfaces them with character provenance. OCR runs only after structural recovery and never reconstructs covered letters from context. Hosted `/v1/unredact` may keep preview limits (copy-size cap cites sha256 + offsets; never invents bytes) but does not lie about capabilities. Never invent letters. Never claim pigment recovery, ESDA, chemical, lab, or forensic certification.\n\nWorks with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import catalog or Worker OpenAPI as a custom tool, GPT Action, HTTP tool, or MCP connector. MCP clients can use the catalog MCP endpoint. Suite mesh: `GET /v1/mesh` PROXY (default OFF). QNS-CD-1.0 cross-map (photon QNS1 packet transfer). Catalog MCP `mesh_*` + FragGate `slug=mesh`.\n";
/**
 * SpectralLock download tracker (Cloudflare Worker).
 *
 * GET  /download?asset=spectrallock-0.3.0.tar.gz
 *      increments KV, serves the tarball via env.ASSETS.fetch
 *      (does not 302 to GitHub)
 * GET  /count   JSON {project, views, downloads, total}. Does not increment.
 * GET  /stats   JSON totals + per-repo + per-branch breakdown
 * POST /event   forks report a download {owner,repo,branch,fork,asset}
 *
 * KV binding DOWNLOADS. Keys: project|owner|repo|branch|fork
 * totalKey() = spectrallock|__total__
 * CORS *. No secrets in this tree.
 * Isolated counter: Worker spectrallock-download-tracker, project spectrallock.
 * Not mixed with any other product.
 *
 * Hosted /v1 never increments DOWNLOADS KV.
 * /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME (HTTP fallback).
 */

const PROJECT = "spectrallock";
const KEYS = isolatedKeys(PROJECT);

const DEFAULT_ASSET = "spectrallock-0.3.0.tar.gz";
const DEFAULT_OWNER = "AzielEliab";
const DEFAULT_REPO = "spectrallock";
const DEFAULT_BRANCH = "main";
const GITHUB_RELEASES = "https://github.com/AzielEliab/spectrallock/releases";
const GITHUB_LATEST = "https://github.com/AzielEliab/spectrallock/releases/latest";
const INSTALL_LINE = "curl -fsSL https://spectrallock-download-tracker.vibelock.workers.dev/install.sh | bash";
const GITHUB_REPO = "https://github.com/AzielEliab/spectrallock";
const HOST = "https://spectrallock-download-tracker.vibelock.workers.dev";

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, HEAD, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept, Authorization, X-Aziel-Runtime-Token, User-Agent",
  };
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders() },
  });
}

function redirect(url) {
  return new Response(null, {
    status: 302,
    headers: { Location: url, ...corsHeaders() },
  });
}

function splitOwnerRepo(value, fallbackOwner, fallbackRepo) {
  if (typeof value === "string" && value.includes("/")) {
    const [o, r] = value.split("/").filter(Boolean);
    if (o && r) return { owner: o, repo: r };
  }
  return { owner: fallbackOwner, repo: fallbackRepo };
}

function parseDims(src) {
  const get = (k) => {
    if (src == null) return null;
    if (typeof src.get === "function") {
      const v = src.get(k);
      return v == null || v === "" ? null : v;
    }
    const v = src[k];
    return v == null || v === "" ? null : v;
  };

  let owner = get("owner") || DEFAULT_OWNER;
  let repo = get("repo") || DEFAULT_REPO;
  if (typeof repo === "string" && repo.includes("/")) {
    const split = splitOwnerRepo(repo, owner, DEFAULT_REPO);
    owner = split.owner;
    repo = split.repo;
  }

  const branch = get("branch") || DEFAULT_BRANCH;
  const tag = get("tag") || "latest";
  const asset = get("asset") || "";

  const forkRaw = get("fork");
  let fork = "0";
  if (forkRaw === 1 || forkRaw === true || forkRaw === "1" || forkRaw === "true") {
    fork = "1";
  } else if (typeof forkRaw === "string" && forkRaw.includes("/")) {
    const split = splitOwnerRepo(forkRaw, owner, repo);
    owner = split.owner;
    repo = split.repo;
    fork = "1";
  } else if (forkRaw != null && forkRaw !== 0 && forkRaw !== false && forkRaw !== "0" && forkRaw !== "false") {
    fork = "1";
  }

  if (`${owner}/${repo}`.toLowerCase() !== `${DEFAULT_OWNER}/${DEFAULT_REPO}`.toLowerCase()) {
    fork = "1";
  }

  return { project: PROJECT, owner, repo, branch, fork, tag, asset };
}

function kvKey(dims) {
  return `${dims.project}|${dims.owner}|${dims.repo}|${dims.branch}|${dims.fork}`;
}

function githubAssetUrl(owner, repo, tag, asset) {
  if (!asset) {
    if (owner === DEFAULT_OWNER && repo === DEFAULT_REPO) return GITHUB_RELEASES;
    return `https://github.com/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/releases`;
  }
  if (!tag || tag === "latest") {
    return `https://github.com/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/releases/latest/download/${encodeURIComponent(asset)}`;
  }
  return `https://github.com/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/releases/download/${encodeURIComponent(tag)}/${encodeURIComponent(asset)}`;
}

function totalKey() {
  return PROJECT + "|__total__";
}


async function bump(env, key) {
  const n = parseInt((await env.DOWNLOADS.get(key)) || "0", 10) + 1;
  await env.DOWNLOADS.put(key, String(n));
  return n;
}

async function incrementSplit(env, humanKey, botKey, request) {
  const cls = classifyRequest(request);
  const splitKey = cls.bucket === "human" ? humanKey : botKey;
  await bump(env, splitKey);
  return cls;
}

async function readHumanBotSplit(env, request) {
  const views = parseInt((await env.DOWNLOADS.get(KEYS.views)) || "0", 10) || 0;
  const downloadsRaw = await env.DOWNLOADS.get(KEYS.total);
  let downloads = parseInt(downloadsRaw || "0", 10);
  if (!Number.isFinite(downloads) || downloads < 0) downloads = 0;
  const viewsHuman = parseInt((await env.DOWNLOADS.get(KEYS.views_human)) || "0", 10) || 0;
  const downloadsHuman = parseInt((await env.DOWNLOADS.get(KEYS.downloads_human)) || "0", 10) || 0;
  const botManagementAvailable = readBotManagement(request).available;
  return shapeHumanBotFields({
    views,
    downloads,
    views_human: viewsHuman,
    downloads_human: downloadsHuman,
    botManagementAvailable,
  });
}

function enrichStatsWithHumanBot(stats, split) {
  return {
    ...stats,
    views_human: split.views_human,
    views_bot: split.views_bot,
    downloads_human: split.downloads_human,
    downloads_bot: split.downloads_bot,
    human: split.human,
    bot: split.bot,
    classification: split.classification,
  };
}

async function increment(env, dims, request) {
  const key = kvKey(dims);
  const n = parseInt((await env.DOWNLOADS.get(key)) || "0", 10) + 1;
  await env.DOWNLOADS.put(key, String(n));
  const tot = parseInt((await env.DOWNLOADS.get(totalKey())) || "0", 10) + 1;
  await env.DOWNLOADS.put(totalKey(), String(tot));
  if (request) await incrementSplit(env, KEYS.downloads_human, KEYS.downloads_bot, request);

  return tot;
}

async function listAllKeys(env) {
  const keys = [];
  let cursor;
  do {
    const page = await env.DOWNLOADS.list(cursor ? { cursor } : {});
    keys.push(...page.keys);
    cursor = page.list_complete ? undefined : page.cursor;
  } while (cursor);
  return keys;
}

async function collectStats(env, request) {
  const keys = await listAllKeys(env);
  let total = 0;
  const by_repo = {};
  const by_branch = {};
  const by_fork = { "0": 0, "1": 0 };
  const breakdown = [];

  for (const k of keys) {
    const name = k.name;
    if (isReservedCounterKey(name, PROJECT)) continue;
    const n = parseInt((await env.DOWNLOADS.get(name)) || "0", 10);
    if (!Number.isFinite(n) || n <= 0) continue;
    const parts = name.split("|");
    if (parts.length < 5) continue;
    const [project, owner, repo, branch, fork] = parts;
    total += n;
    const repoId = `${owner}/${repo}`;
    by_repo[repoId] = (by_repo[repoId] || 0) + n;
    by_branch[branch] = (by_branch[branch] || 0) + n;
    const forkFlag = fork === "1" ? "1" : "0";
    by_fork[forkFlag] = (by_fork[forkFlag] || 0) + n;
    breakdown.push({ project, owner, repo, branch, fork: forkFlag, count: n });
  }

  const totalDirect = parseInt((await env.DOWNLOADS.get(totalKey())) || "0", 10);
  const shown = Number.isFinite(totalDirect) && totalDirect > 0 ? totalDirect : total;
  const __hbViews = parseInt((await env.DOWNLOADS.get(KEYS.views)) || "0", 10) || 0;
  const __hbViewsHuman = parseInt((await env.DOWNLOADS.get(KEYS.views_human)) || "0", 10) || 0;
  const __hbDownloadsHuman = parseInt((await env.DOWNLOADS.get(KEYS.downloads_human)) || "0", 10) || 0;
  const __hbBotMgmt = request ? readBotManagement(request).available : false;

  return {
    ...shapeHumanBotFields({
      views: (typeof views !== 'undefined' ? views : __hbViews),
      downloads: (typeof downloads !== 'undefined' ? downloads : (typeof shown !== 'undefined' ? shown : (typeof total !== 'undefined' ? total : 0))),
      views_human: __hbViewsHuman,
      downloads_human: __hbDownloadsHuman,
      botManagementAvailable: __hbBotMgmt,
    }),

    project: PROJECT,
    total: shown,
    views: parseInt((await env.DOWNLOADS.get(viewsKey())) || "0", 10) || 0,
    downloads: shown,
    by_repo,
    by_branch,
    by_fork,
    breakdown,
    github: (await githubStats(env)),
    note: "Forks identified by GitHub owner/repo. Key layout: project|owner|repo|branch|fork",
  };
}




async function countPayloadAsync(env, request) {
  const stats = await collectStats(env, request);
  const views = Number(stats.views) || 0;
  const downloads = Number(stats.downloads != null ? stats.downloads : stats.total) || 0;
  return shapeCountBody({
    project: PROJECT,
    views,
    downloads,
    total: downloads,
    views_human: stats.views_human,
    downloads_human: stats.downloads_human,
    botManagementAvailable: readBotManagement(request).available,
  });
}

function countPayload(stats) {
  const views = Number(stats && stats.views) || 0;
  const downloads = Number(stats && (stats.downloads != null ? stats.downloads : stats.total)) || 0;
  const total = Number(stats && (stats.total != null ? stats.total : downloads)) || 0;
  return { project: PROJECT, views, downloads, total };
}

function viewsKey() {
  return PROJECT + "|__views__";
}

function githubCacheKey() {
  return PROJECT + "|__github__";
}

async function incrementViews(env, request) {
  const n = parseInt((await env.DOWNLOADS.get(viewsKey())) || "0", 10) + 1;
  await env.DOWNLOADS.put(viewsKey(), String(n));
  if (request) await incrementSplit(env, KEYS.views_human, KEYS.views_bot, request);

  return n;
}

async function githubStats(env) {
  const cached = await env.DOWNLOADS.get(githubCacheKey());
  if (cached) {
    try {
      const obj = JSON.parse(cached);
      if (obj && obj.fetched_at && Date.now() - obj.fetched_at < 5 * 60 * 1000) {
        return obj;
      }
    } catch {
      /* ignore */
    }
  }
  const headers = { "User-Agent": "Mozilla/5.0 SpectralLock-download-tracker", Accept: "application/vnd.github+json" };
  let stars = 0;
  let forks = 0;
  let watchers = 0;
  let release_download_count = 0;
  try {
    const repoRes = await fetch("https://api.github.com/repos/AzielEliab/spectrallock", { headers });
    if (repoRes.ok) {
      const repo = await repoRes.json();
      stars = Number(repo.stargazers_count) || 0;
      forks = Number(repo.forks_count) || 0;
      watchers = Number(repo.subscribers_count != null ? repo.subscribers_count : repo.watchers_count) || 0;
    }
    const relRes = await fetch("https://api.github.com/repos/AzielEliab/spectrallock/releases/latest", { headers });
    if (relRes.ok) {
      const rel = await relRes.json();
      const assets = Array.isArray(rel.assets) ? rel.assets : [];
      release_download_count = assets.reduce((s, a) => s + (Number(a.download_count) || 0), 0);
    }
  } catch {
    /* public API; empty is fine */
  }
  const out = { stars, forks, watchers, release_download_count, fetched_at: Date.now() };
  try {
    await env.DOWNLOADS.put(githubCacheKey(), JSON.stringify(out));
  } catch {
    /* ignore */
  }
  return out;
}

function installScript() {
  return `#!/usr/bin/env bash\n# SpectralLock one-click install. Counted download via this Worker.\nset -euo pipefail\nHOST="${HOST}"\nASSET="${DEFAULT_ASSET}"\nWORKDIR="\${SPECTRALLOCK_HOME:-\$HOME/spectrallock}"\nmkdir -p "\$WORKDIR"\ncd "\$WORKDIR"\necho "Downloading counted tarball from \${HOST}/download (User-Agent Mozilla/5.0)…"\ncurl -fsSL -A 'Mozilla/5.0' "\${HOST}/download?asset=\${ASSET}" -o "\${ASSET}"\ntar -xzf "\${ASSET}"\nDIR=\"\$(find . -maxdepth 1 -type d -name 'spectrallock-*' | head -n 1)\"\nif [ -n "\${DIR}" ]; then\n  cd "\${DIR}"\nfi\npython3 -m venv .venv\n. .venv/bin/activate\npython -m pip install -U pip\npython -m pip install -e .\necho\necho "Installed SpectralLock."\necho "Run:  spectrallock ui"\necho "Then open http://127.0.0.1:8861  (loopback only)"\necho "Author: Aziel Eliab."\n`;
}

async function serveAsset(request, env, asset, { head = false } = {}) {
  if (!env.ASSETS) {
    return json({ error: "assets binding missing" }, 500);
  }
  const assetUrl = new URL("/" + asset, request.url);
  const assetRes = await env.ASSETS.fetch(new Request(assetUrl, { method: "GET" }));
  if (!assetRes.ok) {
    return json({ error: "asset not hosted", asset, status: assetRes.status }, 404);
  }
  const headers = new Headers();
  headers.set("Content-Type", "application/gzip");
  headers.set("Content-Disposition", 'attachment; filename="' + asset.replaceAll('"', "") + '"');
  headers.set("Cache-Control", "private, no-store");
  const len = assetRes.headers.get("Content-Length");
  if (len) headers.set("Content-Length", len);
  for (const [k, v] of Object.entries(corsHeaders())) headers.set(k, v);
  if (head) {
    return new Response(null, { status: 200, headers });
  }
  return new Response(assetRes.body, { status: 200, headers });
}

async function indexHtml(env) {
  const stats = await collectStats(env);
  const downloads = Number(stats.downloads != null ? stats.downloads : stats.total) || 0;
  const views = parseInt((await env.DOWNLOADS.get(viewsKey())) || "0", 10) || 0;
  const v = views.toLocaleString("en-US");
  const n = downloads.toLocaleString("en-US");
  const breakdown = (stats.breakdown || [])
    .map(
      (b) =>
        `<li><code>${b.owner}/${b.repo}</code> branch <code>${b.branch}</code> fork=${b.fork} → ${b.count}</li>`,
    )
    .join("") || "<li>none yet</li>";
  return `<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SpectralLock — Aziel Eliab</title>
<meta name="description" content="Rosetta spectral analysis by Aziel Eliab. Same SpectralLock lenses as Aziel Corpus Library OCR (overlays, ink/page).">
<meta name="author" content="Aziel Eliab">
<link rel="canonical" href="https://spectrallock-download-tracker.vibelock.workers.dev/">
<meta property="og:title" content="SpectralLock — Aziel Eliab">
<meta property="og:description" content="Rosetta spectral analysis by Aziel Eliab. Same SpectralLock lenses as Aziel Corpus Library OCR (overlays, ink/page).">
<meta property="og:url" content="https://spectrallock-download-tracker.vibelock.workers.dev/">
<meta property="og:type" content="website">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "SpectralLock",
  "author": {
    "@type": "Person",
    "name": "Aziel Eliab"
  },
  "codeRepository": "https://github.com/AzielEliab/spectrallock",
  "downloadUrl": "https://spectrallock-download-tracker.vibelock.workers.dev/download",
  "license": "https://www.apache.org/licenses/LICENSE-2.0",
  "url": "https://spectrallock-download-tracker.vibelock.workers.dev/",
  "description": "Rosetta spectral analysis by Aziel Eliab. Same SpectralLock lenses as Aziel Corpus Library OCR (overlays, ink/page)."
}
</script>
<!-- gitbaby-seo -->
<style>
  :root { color-scheme: dark; }
  body { font: 16px/1.45 system-ui, sans-serif; max-width: 42rem; margin: 3rem auto; padding: 0 1.25rem 4rem; background: #0e1014; color: #e8eaef; }
  .brandrow { display: flex; align-items: center; margin: 0 0 1rem; min-height: 48px; }
  .brandmark { width: 40px; height: 40px; border-radius: 10px; object-fit: cover; flex: 0 0 40px; box-shadow: 0 0 0 1px #0003, 0 0 0 1px #c9a227; }
  h1 { font-size: 1.75rem; margin: 0 0 .35rem; }
  .motto { color: #9aa3b2; margin: 0 0 1.5rem; }
  .card { border: 1px solid #2a3140; border-radius: 12px; padding: 1.25rem 1.35rem; background: #151922; }
  .nums { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; margin: 0 0 1rem; }
  .count { font-size: 2.2rem; font-variant-numeric: tabular-nums; font-weight: 700; margin: 0; }
  .count span { display: block; font-size: .95rem; font-weight: 500; color: #9aa3b2; }
  .kid { font-size: 1.05rem; margin: 0 0 1rem; }
  .btns { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; margin: 0 0 .85rem; }
  @media (max-width: 520px) { .btns { grid-template-columns: 1fr; } }
  a.btn, button.btn { display: block; width: 100%; box-sizing: border-box; text-align: center; font: inherit; font-size: 1.2rem; font-weight: 750; padding: 1rem 1.1rem; border-radius: 10px; border: 0; cursor: pointer; text-decoration: none; }
  a.btn.primary { background: #e8eaef; color: #0e1014; }
  button.btn.install { background: #c9a227; color: #14110a; }
  button.btn.install.copied { background: #7dcf9a; color: #0e1014; }
  .meta { margin-top: 1.1rem; color: #9aa3b2; font-size: .92rem; }
  .meta a { color: #c9d4ff; }
  .iso { margin-top: .85rem; font-size: .85rem; color: #7d8696; }
  .banner { border: 1px solid #5c4a1a; background: #241c0d; color: #f0d78c; padding: .85rem 1rem; border-radius: 8px; margin: 0 0 1.2rem; font-size: .92rem; }
  pre { background: #0e1014; padding: .75rem .9rem; overflow: auto; border-radius: 8px; font-size: .82rem; }
  code { font-size: .88rem; }

  .cite { margin-top: 1.4rem; padding-top: 1rem; border-top: 1px solid #2a3140; }
  .cite h2 { font-size: 1.05rem; margin: 0 0 .4rem; }
  .cite p { color: #c5ccd8; font-size: .95rem; }
  .cite a { color: #c9d4ff; }
  #meshStrip { border: 1px solid #c9a227; border-radius: 12px; padding: .85rem 1rem; background: #151922; margin: 0 0 1.2rem; display: flex; flex-wrap: wrap; align-items: center; gap: .7rem 1rem; font-size: .88rem; color: #9aa3b2; }
  #meshStrip .live { color: #e8eaef; }
  #meshStrip .live b { color: #c9a227; font-size: 1.35rem; margin-right: .35rem; }
  #meshStrip .rollup b { color: #c9a227; }
  #meshStrip button { font: 700 .78rem/1 ui-monospace, Menlo, Consolas, monospace; height: 2rem; padding: 0 .75rem; border-radius: 8px; background: #101010; color: #e8eaef; border: 1px solid #c9a227; cursor: pointer; }
  #meshStrip button:hover { background: #241c0d; color: #c9a227; }
  #meshStrip input { width: 10rem; padding: .4rem .55rem; border: 1px solid #c9a227; border-radius: 8px; background: #0e0e0e; color: #e8eaef; font: inherit; }
  #meshProducts { flex-basis: 100%; margin: 0; }
</style>
<body>
  <div class="brandrow"><img class="brandmark" src="/sigil.png" width="40" height="40" alt="" decoding="async"></div>
  <h1>SpectralLock</h1>
  <p class="motto">Rosetta spectral analysis. Same SpectralLock lenses as Aziel Corpus Library OCR (overlays, ink/page). Author Aziel Eliab.</p>
  <p class="banner">RSA-2.0 family. Lenses: zero, tazel, vyrn, uv, rosetta, zen, chaos, balance, candle, indent, lemon. Ink isolates writing; page isolates parchment. Balance never invents marks. Author: Aziel Eliab.</p>
  <div id="meshStrip" aria-label="Suite Live Nodes">
    <div class="live"><b id="meshLiveCount">0</b> Live Nodes</div>
    <div id="meshLine">Suite mesh: off (default). QNM-BUILD-1.0. QNS-CD-1.0. Not an anonymity network.</div>
    <div class="rollup">live <b id="qnmLive">0</b> · locked <b id="qnmLocked">0</b> · isolated <b id="qnmIsolated">0</b></div>
    <div>No Node Gate · No auto-heal · Aziel Eliab only</div>
    <div>
      <input id="meshBearer" type="text" maxlength="80" placeholder="bearer (required to enable)" aria-label="mesh bearer">
      <button id="meshEnable" type="button" title="Enable suite mesh. Declared bearer required. Default off.">Enable</button>
      <button id="meshDisable" type="button" title="Disable suite mesh (always allowed)">Disable</button>
      <button id="meshJoin" type="button" title="Join as spectrallock. Refused while mesh is OFF. No auto-join.">Join</button>
      <button id="meshLeave" type="button" title="Leave this node. No auto-heal.">Leave</button>
    </div>
    <p id="meshProducts">Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · QNS-CD-1.0 cross-map · not AnonBroadcast · not AZMail ring · not a Node Gate · no public qnsd proxy</p>
  </div>
  <div class="card">
    <div class="nums">
      <p class="count">${v}<span>Views</span></p>
      <p class="count">${n}<span>Downloads</span></p>
    </div>
    <p class="kid"><strong>Two big buttons.</strong> Download saves the gzip (the Downloads number goes up). One-click install copies a Terminal command. After it finishes, type <code>spectrallock ui</code>.</p>
    <div class="btns">
      <a class="btn primary dl" href="/download?asset=${DEFAULT_ASSET}">Download</a>
      <button type="button" class="btn install" id="install-btn">One-click install</button>
    </div>
    <pre id="install-cmd">curl -fsSL https://spectrallock-download-tracker.vibelock.workers.dev/install.sh | bash</pre>
    <p class="kid">Then run: <code>spectrallock ui</code> and open http://127.0.0.1:8861 (this computer only).</p>
    <p class="meta">The download count ticks on the Download click. The Worker serves the gzip (HTTP 200). No 302 to GitHub. Forks using this same link are counted automatically. ${DEFAULT_ASSET} — ${n} counted.</p>
    <p class="iso">Isolated counter: Worker <code>spectrallock-download-tracker</code>, project <code>spectrallock</code>, KV <code>SPECTRALLOCK_DOWNLOADS</code>. Not mixed with any other product. /v1 does not increment downloads.</p>
    
    <p class="meta"><a href="/count">JSON count</a> · <a href="/stats">JSON stats</a> · <a href="/openapi.json">OpenAPI</a> · <a href="/v1/mesh">/v1/mesh</a> · <a href="/v1/skill">Skill</a> · <a href="/ai">AI runtime</a> · <a href="${GITHUB_REPO}">GitHub</a> · <a href="${GITHUB_LATEST}">releases</a></p>
    <script>
      (function () {
        var cmd = "curl -fsSL https://spectrallock-download-tracker.vibelock.workers.dev/install.sh | bash";
        var btn = document.getElementById("install-btn");
        var pre = document.getElementById("install-cmd");
        if (!btn) return;
        btn.addEventListener("click", function () {
          function done(ok) {
            btn.textContent = ok ? "Copied! Paste in Terminal, then run spectrallock ui" : "Select the command, copy it, then run spectrallock ui";
            btn.classList.add("copied");
          }
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(cmd).then(function () { done(true); }).catch(function () { done(false); });
          } else {
            done(false);
            if (pre && window.getSelection) {
              var r = document.createRange();
              r.selectNodeContents(pre);
              var sel = window.getSelection();
              sel.removeAllRanges();
              sel.addRange(r);
            }
          }
        });
      })();
      (function () {
        function $(id) { return document.getElementById(id); }
        function meshNum() {
          for (var i = 0; i < arguments.length; i++) {
            var raw = arguments[i];
            if (raw == null || raw === "") continue;
            var n = typeof raw === "number" ? raw : Number(String(raw).replace(/,/g, ""));
            if (Number.isFinite(n) && n >= 0) return Math.floor(n);
          }
          return 0;
        }
        function unwrapMesh(j) {
          if (!j || typeof j !== "object") return {};
          if (j.result && typeof j.result === "object") return Object.assign({}, j, j.result);
          if (j.mesh && typeof j.mesh === "object") return Object.assign({}, j, j.mesh);
          return j;
        }
        function paintMesh(raw) {
          var j = unwrapMesh(raw);
          var on = j.enabled === true || j.enabled === 1 || String(j.status || "").toLowerCase() === "on";
          var r = (j.rollup && typeof j.rollup === "object") ? j.rollup : {};
          var live = on ? meshNum(r.live, j.live_nodes, j.live) : 0;
          var locked = on ? meshNum(r.locked, j.locked_nodes, j.locked) : 0;
          var isolated = on ? meshNum(r.isolated, j.isolated_nodes, j.isolated) : 0;
          $("meshLiveCount").textContent = String(live);
          $("qnmLive").textContent = String(live);
          $("qnmLocked").textContent = String(locked);
          $("qnmIsolated").textContent = String(isolated);
          var line = $("meshLine");
          if (on) line.textContent = "Suite mesh: on · live " + live + " · locked " + locked + " · isolated " + isolated + ". Not an anonymity network.";
          else if (j.status === "unavailable" || (j.ok === false && j.error)) line.textContent = "Suite mesh: off (unavailable). QNM-BUILD-1.0. QNS-CD-1.0. Not an anonymity network.";
          else line.textContent = "Suite mesh: off (default). QNM-BUILD-1.0. QNS-CD-1.0. Not an anonymity network.";
          var products = j.products_present || j.products || [];
          var names = Array.isArray(products) ? products.map(function (p) { return typeof p === "string" ? p : (p && (p.product || p.slug)) || ""; }).filter(Boolean) : [];
          var nodes = Array.isArray(j.nodes) ? j.nodes : [];
          var extra = names.length ? " · products " + names.join(", ") : (nodes.length ? " · " + nodes.length + " node labels" : "");
          $("meshProducts").textContent = "Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · QNS-CD-1.0 cross-map · not AnonBroadcast · not AZMail ring · not a Node Gate · no public qnsd proxy" + extra;
        }
        async function meshGet(path) {
          var r = await fetch(path, { headers: { "user-agent": "Mozilla/5.0", accept: "application/json" } });
          return r.json();
        }
        async function meshPost(path, payload) {
          var r = await fetch(path, { method: "POST", headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" }, body: JSON.stringify(payload || {}) });
          return r.json();
        }
        async function refreshMesh() {
          try {
            var status = await meshGet("/v1/mesh");
            var merged = status;
            var inner = unwrapMesh(status);
            var on = inner.enabled === true;
            if (on) {
              try {
                var nodes = await meshGet("/v1/mesh/nodes");
                merged = Object.assign({}, inner, unwrapMesh(nodes));
              } catch (e) { /* status is enough */ }
            }
            paintMesh(merged);
            var nodeId = sessionStorage.getItem("spectrallock_mesh_node");
            if (on && nodeId) {
              try { await meshPost("/v1/mesh/heartbeat", { node_id: nodeId }); } catch (e) { /* no auto-heal */ }
            }
          } catch (e) {
            paintMesh({ ok: false, enabled: false, status: "unavailable", error: "mesh_unavailable" });
          }
        }
        $("meshEnable").onclick = async function () {
          var bearer = ($("meshBearer").value || "").trim();
          paintMesh(await meshPost("/v1/mesh/enable", bearer ? { bearer: bearer } : {}));
          refreshMesh();
        };
        $("meshDisable").onclick = async function () {
          sessionStorage.removeItem("spectrallock_mesh_node");
          paintMesh(await meshPost("/v1/mesh/disable", {}));
          refreshMesh();
        };
        $("meshJoin").onclick = async function () {
          var j = await meshPost("/v1/mesh/join", { product: "spectrallock", label: "SpectralLock Worker" });
          var inner = unwrapMesh(j);
          var id = inner.node_id || inner.id || (inner.session && inner.session.node_id);
          if (id) sessionStorage.setItem("spectrallock_mesh_node", String(id));
          paintMesh(j);
          refreshMesh();
        };
        $("meshLeave").onclick = async function () {
          var id = sessionStorage.getItem("spectrallock_mesh_node");
          if (id) await meshPost("/v1/mesh/leave", { node_id: id });
          sessionStorage.removeItem("spectrallock_mesh_node");
          refreshMesh();
        };
        window.addEventListener("pagehide", function () {
          var id = sessionStorage.getItem("spectrallock_mesh_node");
          if (!id || typeof navigator.sendBeacon !== "function") return;
          try { navigator.sendBeacon("/v1/mesh/leave", new Blob([JSON.stringify({ node_id: id })], { type: "application/json" })); } catch (e) { /* leave expires in 5 minutes */ }
        });
        refreshMesh();
        setInterval(refreshMesh, 30000);
        document.addEventListener("visibilitychange", function () { if (!document.hidden) refreshMesh(); });
      })();
    </script>
    <h2>Per repo / branch / fork</h2>
    <ul>${breakdown}</ul>
  </div>

<section class="cite" id="cite">
  <h2>How to cite</h2>
  <p>Aziel Eliab. SpectralLock. https://github.com/AzielEliab/spectrallock. https://spectrallock-download-tracker.vibelock.workers.dev.</p>
  <p><a href="https://aziel-runtime.vibelock.workers.dev/">Catalog</a> · <a href="https://github.com/AzielEliab/spectrallock">GitHub</a> · <a href="https://spectrallock-download-tracker.vibelock.workers.dev/download">Download</a> · <a href="https://spectrallock-download-tracker.vibelock.workers.dev/cite.json">cite.json</a></p>
</section>
<!-- /gitbaby-seo -->
</body>
</html>`;
}


function html(body) {
  return new Response(body, {
    headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() },
  });
}

function originOf(request) {
  try {
    return new URL(request.url).origin;
  } catch {
    return HOST;
  }
}

function openapiSpec(request) {
  const origin = originOf(request);
  return {
    openapi: "3.1.0",
    info: {
      title: "SpectralLock runtime",
      version: VERSION,
      summary: "Rosetta spectral analysis. Same SpectralLock lenses as Aziel Corpus Library OCR (overlays, ink/page).",
      description: LIMITATION + " Suite mesh /v1/mesh/* PROXY to aziel-runtime (AZIEL_RUNTIME). Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 hub cite / Worker mesh cross-map only (photon QNS1 packet transfer). No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Not a Softwares-tab product. Aziel Eliab only.",
    },
    servers: [{ url: origin }],
    paths: {
      ...meshOpenApiPaths(),
      "/count": {
        get: {
          operationId: "spectrallockCount",
          summary: "Counted views and downloads. Does not increment KV.",
          responses: {
            "200": {
              description: "{project, views, downloads, total}",
              content: {
                "application/json": {
                  schema: {
                    type: "object",
                    required: ["project", "views", "downloads", "total"],
                    properties: {
                      project: { type: "string" },
                      views: { type: "integer" },
                      downloads: { type: "integer" },
                      total: { type: "integer" },
                    },
                  },
                },
              },
            },
          },
        },
      },
            "/v1/example": { get: { operationId: "spectrallockExample", summary: "Sample JSON payload. Does not increment downloads.", responses: { "200": { description: "OK" } } } },
      "/v1/health": { get: { operationId: "spectrallock_health", summary: "Liveness. Does not increment download KV.", responses: { "200": { description: "ok" } } } },
      "/v1/modes": { get: { operationId: "spectrallock_modes", summary: "List SpectralLock lenses (zero, tazel, vyrn, uv, rosetta, zen, chaos, balance, candle, indent, lemon).", responses: { "200": { description: "modes" } } } },
      "/v1/lenses": { get: { operationId: "spectrallock_lenses", summary: "Alias for /v1/modes — Corpus OCR lens names.", responses: { "200": { description: "lenses" } } } },
      "/v1/targets": { get: { operationId: "spectrallock_targets", summary: "Ink and page targets (Corpus OCR ink/page modes).", responses: { "200": { description: "targets" } } } },
      "/v1/overlay": {
        post: {
          operationId: "spectrallock_overlay",
          summary: "Rosetta spectral overlay preview. PNG b64 in, longest side capped at 256 px. Accepts mode/lens/lenses, target ink|page, and inject true|false (paint, not pigment). Does not increment download KV.",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object", properties: { b64: { type: "string" }, mode: { type: "string", enum: ["zero","tazel","vyrn","uv","rosetta","zen","chaos","balance","candle","indent","lemon"] }, lens: { type: "string" }, lenses: { type: "array", items: { type: "string" } }, target: { type: "string", enum: ["ink", "page"] }, inject: { type: "boolean", description: "False-color membership tint. Not recovered pigment. Zero ignores the switch." } }, required: ["b64"] } } } },
          responses: { "200": { description: "png_b64 + metadata" } },
        },
      },
      "/v1/unredact": {
        get: { operationId: "spectrallock_unredact_ops", summary: "Honest unredact / leftover-bytes ops. Does not increment downloads.", responses: { "200": { description: "ops + honesty banner" } } },
        post: {
          operationId: "spectrallock_unredact",
          summary: "Locate leftover / historical page bytes. Returns revision_graph (startxref/Prev edges + per-revision tip-cut copies). Opaque rewrite with nothing left refuses SL-UNREDACT-OPAQUE. Never invents letters. OCR only after structural recovery.",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object", properties: { b64: { type: "string" }, op: { type: "string", enum: ["locate", "lift", "recover", "refuse"] }, query: { type: "string" }, twin_b64: { type: "string", description: "Optional second document (neighboring release). Twin-page compare of operator text + identifiers. Not a transcript." }, twin: { type: "string" } }, required: ["b64"] } } } },
          responses: { "200": { description: "findings including revision_graph (revisions[].copy tip-cut PDF/embeds; edges with replaced|overlaid|detached|sanitized rewrite). Hosted may omit large copy b64 and cite sha256+offsets — never invents bytes." } },
        },
      },
      "/v1/lift": { post: { operationId: "spectrallock_lift", summary: "Alias for unredact lift (non-opaque residual or leftover recover).", responses: { "200": { description: "findings" } } } },
      "/v1/redact-locate": { post: { operationId: "spectrallock_redact_locate", summary: "Alias for unredact locate.", responses: { "200": { description: "findings" } } } },
    },
  };
}

function aiHelpPage(request) {
  const origin = originOf(request);
  return `<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SpectralLock — AI runtime</title>
<style>
  :root { color-scheme: dark; }
  body { font: 16px/1.45 system-ui, sans-serif; max-width: 44rem; margin: 3rem auto; padding: 0 1.25rem; background: #0b0b0b; color: #e8e0d0; }
  a { color: #c9a227; }
  code, pre { background: #141414; padding: .15rem .35rem; border-radius: 4px; }
  pre { padding: .85rem 1rem; overflow: auto; }
  .banner { border: 1px solid #5c4a1a; background: #241c0d; color: #f0d78c; padding: .85rem 1rem; border-radius: 8px; }
</style>
<body>
<h1>SpectralLock runtime</h1>
<p class="banner">${LIMITATION}</p>
<p>OpenAPI: <a href="${origin}/openapi.json">${origin}/openapi.json</a></p>
<p>Catalog: <a href="https://aziel-runtime.vibelock.workers.dev/">aziel-runtime.vibelock.workers.dev</a> (catalog <code>mesh_*</code> + FragGate <code>slug=mesh</code>).</p>
<p>Suite mesh: <a href="${origin}/v1/mesh">${origin}/v1/mesh</a> PROXY to aziel-runtime. Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 hub cite / Worker mesh cross-map only (photon QNS1 packet transfer). No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Not a Softwares-tab product. Author: Aziel Eliab only.</p>
<pre>curl ${origin}/v1/health
curl ${origin}/v1/modes
curl ${origin}/v1/mesh
curl -X POST ${origin}/v1/overlay -H 'content-type: application/json' \\
  -d '{"mode":"rosetta","target":"ink","inject":true,"b64":"<png-base64>"}'
</pre>
<p>Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants.</p>
<p>GET/POST under <code>/v1</code> never increment the download counter. Hosted overlay is a simplified preview (max 256 px). Full pipeline is the Python package.</p>
<p><a href="/">Downloads</a></p>
</body></html>`;
}

async function handleRuntime(request, url) {
  const path = url.pathname.replace(/\/+$/, "") || "/";
  if (path === "/v1/mesh" || path.startsWith("/v1/mesh/")) return null;
  if (path === "/v1/health" && request.method === "GET") {
    return json({
      ok: true, author: "Aziel Eliab",
      product: "spectrallock",
      version: VERSION,
      runtime: true,
      kv_increment: false,
      rosetta_spectral_analysis: true,
      corpus_ocr_aligned: true,
      lenses: ["zero", "tazel", "vyrn", "uv", "rosetta", "zen", "chaos", "balance", "candle", "indent", "lemon"],
      targets: ["ink", "page"],
      inject: [true, false],
      unredact: listUnredact(),
      pigment_recovery: false,
      synthetic_uv: true,
      limitation: LIMITATION,
      mesh: meshPointer(),
    });
  }
  if ((path === "/v1/example" || path === "/v1/example/") && (request.method === "GET" || request.method === "HEAD")) {
    return json({
      ok: true,
      product: "spectrallock",
      author: "Aziel Eliab",
      example: EXAMPLE_PAYLOAD,
      note: "Sample payload only. Does not increment downloads.",
    });
  }


  if (path === "/v1/skill" && request.method === "GET") {
    return new Response(SKILL_MARKDOWN, {
      status: 200,
      headers: {
        "Content-Type": "text/markdown; charset=utf-8",
        "Cache-Control": "private, no-store",
        "X-KV-Increment": "false",
        "Access-Control-Allow-Origin": "*",
      },
    });
  }

  if ((path === "/v1/modes" || path === "/v1/lenses") && request.method === "GET") {
    return json({
      product: "spectrallock",
      version: VERSION,
      author: "Aziel Eliab",
      rosetta_spectral_analysis: true,
      corpus_ocr_aligned: true,
      modes: MODES,
      lenses: MODES,
      targets: TARGETS,
      unredact: listUnredact(),
      advisory: LIMITATION,
    });
  }
  if (path === "/v1/targets" && request.method === "GET") {
    return json({
      product: "spectrallock",
      version: VERSION,
      author: "Aziel Eliab",
      targets: TARGETS,
      advisory: LIMITATION,
    });
  }
  if (path === "/openapi.json" && request.method === "GET") {
    return json(openapiSpec(request));
  }
  if ((path === "/ai" || url.pathname === "/ai/") && request.method === "GET") {
    return html(aiHelpPage(request));
  }
  if (path === "/v1/overlay" && request.method === "POST") {
    let body;
    try { body = await request.json(); } catch {
      return json({ error: "JSON body required", limitation: LIMITATION }, 400);
    }
    const b64 = body && (body.b64 || body.image);
    const mode = body && (body.mode || body.lens);
    if (!b64) return json({ error: "b64 PNG required", limitation: LIMITATION }, 400);
    if (String(b64).length > 2_000_000) {
      return json({ error: "image too large for hosted preview", limitation: LIMITATION }, 413);
    }
    const result = await overlayFromB64(b64, mode, {
      lens: body && body.lens,
      lenses: body && body.lenses,
      target: body && (body.target || body.polarity),
      inject: body && body.inject,
      no_inject: body && body.no_inject,
      tint: body && body.tint,
    });
    const status = result.error ? 400 : 200;
    return json(result, status);
  }
  if (path === "/v1/unredact" && request.method === "GET") {
    return json({
      product: "spectrallock",
      version: VERSION,
      author: "Aziel Eliab",
      unredact: listUnredact(),
      advisory: UNREDACT_NOTE,
      kv_increment: false,
    });
  }
  if ((path === "/v1/unredact" || path === "/v1/lift" || path === "/v1/redact-locate") && request.method === "POST") {
    let body;
    try { body = await request.json(); } catch {
      return json({ error: "JSON body required", limitation: UNREDACT_NOTE }, 400);
    }
    const b64 = body && (body.b64 || body.image || body.pdf_b64);
    if (!b64) return json({ error: "b64 PDF or PNG required", limitation: UNREDACT_NOTE }, 400);
    if (String(b64).length > 2_000_000) {
      return json({ error: "payload too large for hosted preview", limitation: UNREDACT_NOTE }, 413);
    }
    const op = path === "/v1/lift" ? "lift" : path === "/v1/redact-locate" ? "locate" : (body.op || "locate");
    const result = await unredactFromB64(b64, { op, query: body.query, verb: body.verb, twin_b64: body.twin_b64 || body.twin });
    const status = result.error ? 400 : (result.refuse_code && result.stop && op === "lift" ? 409 : 200);
    return json(result, status);
  }
  if (path.startsWith("/v1/") || path === "/v1") {
    return json({ error: "not found", hint: "GET /v1/health /v1/lenses /v1/targets /v1/unredact /v1/mesh ; POST /v1/overlay /v1/unredact /v1/lift", limitation: LIMITATION }, 404);
  }
  return null;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    if (request.method === "HEAD") {
      const getReq = new Request(request.url, { method: "GET", headers: request.headers });
      const res = await this.fetch(getReq, env);
      return new Response(null, { status: res.status, headers: res.headers });
    }

    const mesh = await handleMeshApi(request, url, env);
    if (mesh) return mesh;

    const runtime = await handleRuntime(request, url);
    if (runtime) return runtime;

    if ((url.pathname === "/install.sh" || url.pathname === "/install.sh/") && request.method === "GET") {
      return new Response(installScript(), {
        status: 200,
        headers: {
          "Content-Type": "text/x-shellscript; charset=utf-8",
          "Cache-Control": "private, no-store",
          ...corsHeaders(),
        },
      });
    }

    if (url.pathname === "/" && request.method === "GET") {
      await incrementViews(env, request);
      return new Response(await indexHtml(env), {
        headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() },
      });
    }

    if ((url.pathname === "/count" || url.pathname === "/count/") && request.method === "GET") {
      return json(await countPayloadAsync(env, request));
    }

    if (url.pathname === "/stats" && request.method === "GET") {
      return json(await collectStats(env, request));
    }

    if (url.pathname === "/event" && request.method === "POST") {
      let body;
      try {
        body = await request.json();
      } catch {
        return json({ error: "JSON body required" }, 400);
      }
      const dims = parseDims(body || {});
      const count = await increment(env, dims, request);
      return json({
        ok: true,
        key: kvKey(dims),
        count,
        owner: dims.owner,
        repo: dims.repo,
        branch: dims.branch,
        fork: dims.fork,
        asset: dims.asset || null,
      });
    }

    if (url.pathname === "/go" && (request.method === "GET" || request.method === "HEAD")) {
      const dims = parseDims(url.searchParams);
      const asset = dims.asset || DEFAULT_ASSET;
      dims.asset = asset;
      if (request.method === "GET") await increment(env, dims, request);
      return serveAsset(request, env, asset, { head: request.method === "HEAD" });
    }

    if ((url.pathname === "/download" || url.pathname.startsWith("/download/")) && (request.method === "GET" || request.method === "HEAD")) {
      const dims = parseDims(url.searchParams);
      if (!dims.asset && url.pathname.startsWith("/download/")) {
        dims.asset = decodeURIComponent(url.pathname.slice("/download/".length));
      }
      const asset = dims.asset || DEFAULT_ASSET;
      dims.asset = asset;
      if (request.method === "GET") await increment(env, dims, request);
      return serveAsset(request, env, asset, { head: request.method === "HEAD" });
    }


    // gitbaby-seo-routes
    if ((url.pathname === "/robots.txt" || url.pathname === "/robots.txt/") && request.method === "GET") {
      const body = "User-agent: *\nAllow: /\nSitemap: " + HOST + "/sitemap.xml\n";
      return new Response(body, {
        status: 200,
        headers: { "Content-Type": "text/plain; charset=utf-8", ...corsHeaders() },
      });
    }
    if ((url.pathname === "/sitemap.xml" || url.pathname === "/sitemap.xml/") && request.method === "GET") {
      const locs = [HOST + "/", HOST + "/download", HOST + "/install.sh", HOST + "/v1/skill", HOST + "/v1/mesh", HOST + "/openapi.json", GITHUB_REPO];
      const xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + locs.map((u) => "  <url><loc>" + u + "</loc></url>").join("\n")
        + "\n</urlset>\n";
      return new Response(xml, {
        status: 200,
        headers: { "Content-Type": "application/xml; charset=utf-8", ...corsHeaders() },
      });
    }
    if ((url.pathname === "/cite.json" || url.pathname === "/cite.json/") && request.method === "GET") {
      return json({"author": "Aziel Eliab", "title": "SpectralLock", "github": "https://github.com/AzielEliab/spectrallock", "download": "https://spectrallock-download-tracker.vibelock.workers.dev/download", "doi": null, "license": "Apache-2.0", "catalog": "https://aziel-runtime.vibelock.workers.dev/"});
    }
    // /gitbaby-seo-routes
    return json({ error: "not found" }, 404);
  },
};
