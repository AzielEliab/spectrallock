/* SpectralLock local UI. Loopback only. No telemetry. */
const LIVE = ["zero","tazel","vyrn","uv","rosetta","zen","chaos","balance"];
const fileInput = document.getElementById("file");
const drop = document.getElementById("drop");
const btns = document.getElementById("btns");
const before = document.getElementById("before");
const after = document.getElementById("after");
const afterLabel = document.getElementById("after-label");
const meta = document.getElementById("meta");
const fname = document.getElementById("fname");
const addFileBtn = document.getElementById("add-file");
const exportBtn = document.getElementById("export");

let sourceFile = null;
let overlayBlob = null;
let active = "rosetta";
let objectUrls = [];

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
}

LIVE.forEach((id) => {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "mode" + (id === active ? " active" : "");
  b.textContent = id;
  b.dataset.mode = id;
  b.addEventListener("click", () => {
    active = id;
    document.querySelectorAll("button.mode").forEach((el) => {
      el.classList.toggle("active", el.dataset.mode === id);
    });
    run();
  });
  btns.appendChild(b);
});

function setFile(file) {
  if (!file) return;
  sourceFile = file;
  overlayBlob = null;
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

exportBtn.addEventListener("click", () => {
  if (!overlayBlob) return;
  const stem = stemFromName(sourceFile && sourceFile.name);
  const a = document.createElement("a");
  const u = URL.createObjectURL(overlayBlob);
  a.href = u;
  a.download = "spectrallock-" + active + "-" + stem + ".png";
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(u), 2000);
});

async function run() {
  if (!sourceFile) return;
  document.querySelectorAll("button.mode").forEach((el) => { el.disabled = true; });
  addFileBtn.disabled = true;
  setExportEnabled(false);
  meta.textContent = "working…";
  try {
    const fd = new FormData();
    fd.append("mode", active);
    fd.append("file", sourceFile, sourceFile.name || "page.png");
    const res = await fetch("/api/overlay", { method: "POST", body: fd });
    if (!res.ok) {
      const t = await res.text();
      meta.textContent = "error: " + t;
      overlayBlob = null;
      return;
    }
    const out = await res.blob();
    overlayBlob = out;
    const u = URL.createObjectURL(out);
    objectUrls.push(u);
    after.src = u;
    afterLabel.textContent = "· " + active;
    const paper = res.headers.get("X-SpectralLock-Paper") || "";
    meta.textContent = active + (paper ? " (" + paper + ")" : "") +
      " — advisory overlay, not forensic proof.";
    setExportEnabled(true);
  } catch (err) {
    meta.textContent = String(err);
    overlayBlob = null;
  } finally {
    document.querySelectorAll("button.mode").forEach((el) => { el.disabled = false; });
    addFileBtn.disabled = false;
    if (!overlayBlob) setExportEnabled(false);
  }
}
