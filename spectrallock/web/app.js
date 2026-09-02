/* SpectralLock local UI. Loopback only. No telemetry. */
const LIVE = ["zero","tazel","vyrn","uv","rosetta","zen","chaos","balance"];
const KID = {
  zero: "Clearer lines",
  tazel: "Lift green-gold",
  vyrn: "Lift magenta",
  uv: "Fake UV look",
  rosetta: "Mix of three",
  zen: "Even mix of four",
  chaos: "Strong mix",
  balance: "Blend two mixes",
};
const PAPERS = {
  zero: "ZSA-1.0", tazel: "TSA-1.0", vyrn: "VSA-1.0", uv: "UVSA-1.0",
  rosetta: "RSA-2.0", zen: "ZENA-1.0", chaos: "CSA-1.0", balance: "BSA",
};

const fileInput = document.getElementById("file");
const drop = document.getElementById("drop");
const btns = document.getElementById("btns");
const before = document.getElementById("before");
const after = document.getElementById("after");
const afterLabel = document.getElementById("after-label");
const meta = document.getElementById("meta");
const fname = document.getElementById("fname");
const addFileBtn = document.getElementById("add-file");
const sampleBtn = document.getElementById("sample");
const exportBtn = document.getElementById("export");
const verifyBtn = document.getElementById("verify");
const receiptEl = document.getElementById("receipt");
const receiptBody = document.getElementById("receipt-body");
const compare = document.getElementById("compare");
const levelSimple = document.getElementById("level-simple");
const levelAdvanced = document.getElementById("level-advanced");
const viewSide = document.getElementById("view-side");
const viewOverlay = document.getElementById("view-overlay");

let sourceFile = null;
let overlayBlob = null;
let lastReceipt = null;
let active = "rosetta";
let simple = true;
let objectUrls = [];
let modeMeta = {};

function forgetUrls() {
  for (const u of objectUrls) URL.revokeObjectURL(u);
  objectUrls = [];
}

function stemFromName(name) {
  const base = String(name || "page").split(/[\\/]/).pop() || "page";
  const cut = base.replace(/\.[^.]+$/, "");
  return cut || "page";
}

function setExportEnabled(on) {
  exportBtn.disabled = !on;
  verifyBtn.disabled = !on;
}

function modeLabel(id) {
  if (simple) return (modeMeta[id] && modeMeta[id].kid_label) || KID[id] || id;
  const paper = (modeMeta[id] && modeMeta[id].paper) || PAPERS[id] || "";
  return paper ? id + " (" + paper + ")" : id;
}

function paintModeButtons() {
  document.querySelectorAll("button.mode").forEach((el) => {
    const id = el.dataset.mode;
    el.textContent = modeLabel(id);
    el.title = (modeMeta[id] && (simple ? modeMeta[id].kid_hint : modeMeta[id].summary)) || "";
    el.classList.toggle("active", id === active);
  });
}

LIVE.forEach((id) => {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "mode" + (id === active ? " active" : "");
  b.dataset.mode = id;
  b.textContent = modeLabel(id);
  b.addEventListener("click", () => {
    active = id;
    paintModeButtons();
    run();
  });
  btns.appendChild(b);
});

fetch("/api/modes").then((r) => r.json()).then((payload) => {
  (payload.modes || []).forEach((row) => { modeMeta[row.id] = row; });
  paintModeButtons();
}).catch(() => {});

function setFile(file) {
  if (!file) return;
  sourceFile = file;
  overlayBlob = null;
  lastReceipt = null;
  receiptEl.hidden = true;
  setExportEnabled(false);
  fname.textContent = file.name + " · " + Math.round(file.size / 1024) + " KiB";
  forgetUrls();
  const u = URL.createObjectURL(file);
  objectUrls.push(u);
  before.src = u;
  after.removeAttribute("src");
  afterLabel.textContent = "";
  run();
}

addFileBtn.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => setFile(fileInput.files[0]));
["dragenter","dragover"].forEach((ev) => {
  drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("over"); });
});
["dragleave","drop"].forEach((ev) => {
  drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("over"); });
});
drop.addEventListener("drop", (e) => {
  const f = e.dataTransfer.files && e.dataTransfer.files[0];
  setFile(f);
});

sampleBtn.addEventListener("click", async () => {
  meta.textContent = "loading sample page…";
  try {
    const res = await fetch("/api/sample");
    if (!res.ok) {
      meta.textContent = "error: could not load sample page";
      return;
    }
    const blob = await res.blob();
    const file = new File([blob], "synthetic_page.png", { type: "image/png" });
    setFile(file);
  } catch (err) {
    meta.textContent = String(err);
  }
});

function downloadBlob(blob, name) {
  const a = document.createElement("a");
  const u = URL.createObjectURL(blob);
  a.href = u;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(u), 2000);
}

exportBtn.addEventListener("click", () => {
  if (!overlayBlob) return;
  const stem = stemFromName(sourceFile && sourceFile.name);
  const base = "spectrallock-" + active + "-" + stem;
  downloadBlob(overlayBlob, base + ".png");
  const sidecar = lastReceipt || {
    mode: active,
    limitation: "Advisory overlay. Not forensic proof.",
  };
  const json = new Blob([JSON.stringify(sidecar, null, 2) + "\n"], { type: "application/json" });
  setTimeout(() => downloadBlob(json, base + ".json"), 250);
});

function receiptText(rec) {
  if (!rec) return "";
  return [
    "mode: " + rec.mode,
    "paper: " + rec.paper,
    "sha256_in: " + rec.sha256_in,
    "sha256_out: " + rec.sha256_out,
    "size_in: " + rec.size_in,
    "size_out: " + rec.size_out,
    rec.limitation || "",
  ].join("\n");
}

verifyBtn.addEventListener("click", () => {
  if (!lastReceipt) return;
  receiptEl.hidden = !receiptEl.hidden;
  receiptBody.textContent = receiptText(lastReceipt);
});

levelSimple.addEventListener("click", () => {
  simple = true;
  levelSimple.classList.add("active");
  levelAdvanced.classList.remove("active");
  paintModeButtons();
});
levelAdvanced.addEventListener("click", () => {
  simple = false;
  levelAdvanced.classList.add("active");
  levelSimple.classList.remove("active");
  paintModeButtons();
});
viewSide.addEventListener("click", () => {
  compare.classList.remove("overlay-only");
  viewSide.classList.add("active");
  viewOverlay.classList.remove("active");
});
viewOverlay.addEventListener("click", () => {
  compare.classList.add("overlay-only");
  viewOverlay.classList.add("active");
  viewSide.classList.remove("active");
});

async function run() {
  if (!sourceFile) return;
  document.querySelectorAll("button.mode").forEach((el) => { el.disabled = true; });
  addFileBtn.disabled = true;
  sampleBtn.disabled = true;
  setExportEnabled(false);
  receiptEl.hidden = true;
  meta.textContent = "working…";
  try {
    const fd = new FormData();
    fd.append("mode", active);
    fd.append("file", sourceFile, sourceFile.name || "page.png");
    const res = await fetch("/api/overlay", { method: "POST", body: fd });
    if (!res.ok) {
      let msg = await res.text();
      try {
        const err = JSON.parse(msg);
        msg = err.error || msg;
      } catch (_) {}
      meta.textContent = "error: " + msg;
      overlayBlob = null;
      lastReceipt = null;
      return;
    }
    const out = await res.blob();
    overlayBlob = out;
    lastReceipt = {
      mode: res.headers.get("X-SpectralLock-Mode") || active,
      paper: res.headers.get("X-SpectralLock-Paper") || "",
      sha256_in: res.headers.get("X-SpectralLock-Sha256-In") || "",
      sha256_out: res.headers.get("X-SpectralLock-Sha256-Out") || "",
      size_in: res.headers.get("X-SpectralLock-Size-In") || "",
      size_out: res.headers.get("X-SpectralLock-Size-Out") || "",
      limitation: "Advisory digital overlays on photographs of manuscript pages. Not a lab spectrometer, not forensic proof, not OCR.",
      product: "spectrallock",
    };
    const u = URL.createObjectURL(out);
    objectUrls.push(u);
    after.src = u;
    afterLabel.textContent = "· " + (simple ? modeLabel(active) : active);
    const paper = lastReceipt.paper;
    meta.textContent = active + (paper ? " (" + paper + ")" : "") +
      " — advisory overlay, not forensic proof.";
    setExportEnabled(true);
  } catch (err) {
    meta.textContent = String(err);
    overlayBlob = null;
    lastReceipt = null;
  } finally {
    document.querySelectorAll("button.mode").forEach((el) => { el.disabled = false; });
    addFileBtn.disabled = false;
    sampleBtn.disabled = false;
    if (!overlayBlob) setExportEnabled(false);
  }
}
