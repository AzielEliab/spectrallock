/**
 * SpectralLock discovery-surface copy: keep positive definitions,
 * refuse SEO not-catalogs and blocked-from / Zenodo-ban lines.
 * Author: Aziel Eliab. Apache-2.0.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { LIMITATION, INJECT_NOTE, UNREDACT_NOTE, HANDWRITING_NOTE } from "../src/overlay.js";
import worker from "../src/index.js";

const root = join(dirname(fileURLToPath(import.meta.url)), "../../..");

const DISCOVERY_FILES = [
  "README.md",
  "SKILL.md",
  "docs/llms.txt",
  "docs/ai.txt",
  "docs/cite.json",
  "workers/download-tracker/README.md",
  "workers/download-tracker/src/index.js",
  "workers/download-tracker/src/mesh.js",
];

const FORBIDDEN = [
  /THIS IS NOT/i,
  /What this is not/i,
  /What it is not/i,
  /does not really/i,
  /what not to say/i,
  /≠/,
  /blocked from/i,
  /blockedExamples/,
  /SEO mills are blocked/i,
  /CNS-ZENODO/i,
  /zenodo[- ]?ban/i,
  /IP-BAN/i,
  /Zenodo refused/i,
  /Not a Softwares-tab product/i,
  /Not anonymity/i,
  /Not an anonymity network/i,
  /not ESDA/i,
  /not a lamp/i,
  /not a lab/i,
  /not a court/i,
  /not writer identity/i,
];

const REQUIRED = [
  /Rosetta spectral analysis/i,
  /Aziel Corpus Library OCR/i,
  /spectrallock-download-tracker\.vibelock\.workers\.dev/,
  /Aziel Eliab/,
  /never invent/i,
  /refuses/,
];

const joined = DISCOVERY_FILES.map((rel) => {
  const text = readFileSync(join(root, rel), "utf8");
  return { rel, text };
});

for (const { rel, text } of joined) {
  for (const re of FORBIDDEN) {
    assert.equal(re.test(text), false, `${rel} still has SEO not-phrase / ban-catalog: ${re}`);
  }
}

const all = joined.map((f) => f.text).join("\n");
for (const re of REQUIRED) {
  assert.equal(re.test(all), true, `discovery surfaces lost defining copy: ${re}`);
}

for (const [name, text] of [
  ["LIMITATION", LIMITATION],
  ["INJECT_NOTE", INJECT_NOTE],
  ["UNREDACT_NOTE", UNREDACT_NOTE],
  ["HANDWRITING_NOTE", HANDWRITING_NOTE],
]) {
  for (const re of FORBIDDEN) {
    assert.equal(re.test(text), false, `${name} still has SEO not-phrase: ${re}`);
  }
}

assert.match(LIMITATION, /Rosetta spectral analysis/i);
assert.match(LIMITATION, /never invents marks/i);
assert.match(LIMITATION, /refuses \(SL-UNREDACT-OPAQUE\)/);
assert.match(LIMITATION, /Aziel Eliab/);
assert.doesNotMatch(LIMITATION, /THIS IS NOT/i);
assert.doesNotMatch(LIMITATION, /≠/);

function memoryKv() {
  return {
    async get() {
      return "0";
    },
    async put() {},
    async list() {
      return { keys: [], list_complete: true };
    },
  };
}

const env = { DOWNLOADS: memoryKv() };
const origin = "https://spectrallock-download-tracker.vibelock.workers.dev";

const skill = await worker.fetch(
  new Request(origin + "/v1/skill", { headers: { "User-Agent": "Mozilla/5.0" } }),
  env,
);
const skillText = await skill.text();
assert.equal(skill.status, 200);
assert.match(skillText, /Rosetta spectral analysis/i);
assert.match(skillText, /https:\/\/spectrallock-download-tracker\.vibelock\.workers\.dev/);
assert.match(skillText, /\*\*THIS IS:\*\*/);
assert.doesNotMatch(skillText, /THIS IS NOT/);
assert.doesNotMatch(skillText, /≠/);
assert.doesNotMatch(skillText, /Not a Softwares-tab product/i);

const llms = await worker.fetch(
  new Request(origin + "/llms.txt", { headers: { "User-Agent": "Mozilla/5.0" } }),
  env,
);
const llmsText = await llms.text();
assert.equal(llms.status, 200);
assert.match(llmsText, /Rosetta spectral analysis/i);
assert.match(llmsText, /https:\/\/spectrallock-download-tracker\.vibelock\.workers\.dev/);
assert.doesNotMatch(llmsText, /What this is not/i);
assert.doesNotMatch(llmsText, /blocked from/i);
assert.doesNotMatch(llmsText, /≠/);

const ai = await worker.fetch(
  new Request(origin + "/ai.txt", { headers: { "User-Agent": "Mozilla/5.0" } }),
  env,
);
const aiText = await ai.text();
assert.equal(ai.status, 200);
assert.match(aiText, /Rosetta spectral analysis/i);
assert.match(aiText, /Aziel Eliab only/);
assert.doesNotMatch(aiText, /THIS IS NOT/);
assert.doesNotMatch(aiText, /What this is not/i);

const cite = await worker.fetch(
  new Request(origin + "/cite.json", { headers: { "User-Agent": "Mozilla/5.0" } }),
  env,
);
const citeJson = await cite.json();
assert.equal(cite.status, 200);
assert.equal(citeJson.author, "Aziel Eliab");
assert.equal(citeJson.live, origin + "/");
assert.match(citeJson.honesty, /never invent/i);
assert.doesNotMatch(JSON.stringify(citeJson), /THIS IS NOT/i);
assert.equal(citeJson.not, undefined);

const home = await worker.fetch(
  new Request(origin + "/", { headers: { "User-Agent": "Mozilla/5.0" } }),
  env,
);
const homeText = await home.text();
assert.equal(home.status, 200);
assert.match(homeText, /Rosetta spectral analysis/i);
assert.doesNotMatch(homeText, /THIS IS NOT/);
assert.doesNotMatch(homeText, /Not an anonymity network/);
assert.doesNotMatch(homeText, /Not a Softwares-tab product/i);

console.log("verify-discovery-copy: SEO/llms/ai/cite keep definitions; not-catalogs and ban-lines gone");
