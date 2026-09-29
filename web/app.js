const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const pct = (x, d = 1) => (x * 100).toFixed(d) + "%";
const LABELS = { age: "Age", sex: "Sex", cp: "Chest pain", trestbps: "Resting BP", chol: "Cholesterol", fbs: "Fasting sugar",
  restecg: "Resting ECG", thalach: "Max HR", exang: "Exercise angina", oldpeak: "ST depression", slope: "ST slope",
  ca: "Vessels (ca)", thal: "Thalassemia" };
const MODEL_NAMES = { svm: "RBF SVM", logreg: "Logistic regression", rf: "Random forest", xgboost: "XGBoost",
  extratrees: "Extra trees", voting: "Soft-voting ensemble", stacking: "Stacking ensemble" };
const CP = { 1: "Typical", 2: "Atypical", 3: "Non-anginal", 4: "Asymptomatic" };
const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

// ---------- data cache ----------
let metricsP;
const getMetrics = () => (metricsP ??= fetch("/api/metrics").then((r) => r.json()));

// ---------- toast ----------
function toast(msg) {
  const t = $("#toast"); t.textContent = msg; t.classList.add("show");
  clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove("show"), 2200);
}

// ---------- theme ----------
const renderers = new Map(); // chart id -> () => config, so charts can re-theme
const charts = {};
function draw(id, build) {
  renderers.set(id, build);
  charts[id]?.destroy();
  charts[id] = new Chart($(id), build());
}
$("#theme").addEventListener("click", () => {
  const dark = document.documentElement.classList.toggle("dark");
  try { localStorage.setItem("theme", dark ? "dark" : "light"); } catch (e) {}
  setTimeout(() => renderers.forEach((b, id) => { if ($(id)?.offsetParent) draw(id, b); }), 210);
});
$("#menu").addEventListener("click", () => $("#links").classList.toggle("open"));

function chartDefaults() {
  Chart.defaults.font.family = "Geist, ui-sans-serif, system-ui, sans-serif";
  Chart.defaults.font.size = 11;
  Chart.defaults.color = css("--subtle");
  Chart.defaults.animation.duration = reduced ? 0 : 900;
  Chart.defaults.animation.easing = "easeOutQuart";
  Object.assign(Chart.defaults.plugins.tooltip, {
    backgroundColor: css("--surface"), titleColor: css("--muted"), bodyColor: css("--ink"),
    borderColor: css("--hair"), borderWidth: 1, padding: 10, cornerRadius: 8, displayColors: false,
  });
}
const grid = () => ({ color: css("--hair"), drawTicks: false });
const axes = (x, y) => ({
  x: { type: "linear", min: 0, max: 1, grid: grid(), border: { color: css("--hair") }, title: { display: true, text: x }, ticks: { padding: 6 } },
  y: { min: 0, max: 1, grid: grid(), border: { color: css("--hair") }, title: { display: true, text: y }, ticks: { padding: 6 } },
});
const diag = () => ({ data: [{ x: 0, y: 0 }, { x: 1, y: 1 }], borderColor: css("--hairS"), borderDash: [4, 4], pointRadius: 0, borderWidth: 1 });

// ---------- animations ----------
const io = new IntersectionObserver((entries) => entries.forEach((e) => {
  if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
}), { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
function observeReveals(root) {
  $$(".reveal:not(.in)", root).forEach((el, i) => { el.style.setProperty("--d", `${Math.min(i % 4, 3) * 70}ms`); io.observe(el); });
}
function countUp(el, to, fmt, ms = 1200) {
  el.classList.remove("skeleton");
  if (reduced) { el.textContent = fmt(to); return; }
  const t0 = performance.now();
  const step = (t) => {
    const k = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(1 - k, 3);
    el.textContent = fmt(to * e);
    if (k < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

// ---------- router ----------
const loaders = { home: loadHome, predict: () => {}, performance: loadPerformance, data: loadData, history: loadHistory };
function route() {
  const name = (location.hash.replace("#/", "") || "home").split("?")[0];
  const view = loaders[name] ? name : "home";
  $$(".view").forEach((v) => v.classList.toggle("active", v.dataset.view === view));
  $$(".links a[data-route]").forEach((a) => a.classList.toggle("active", a.dataset.route === view));
  $("#links").classList.remove("open");
  window.scrollTo({ top: 0, behavior: "instant" });
  document.title = view === "home" ? "CardioRisk" : `${view[0].toUpperCase() + view.slice(1)} · CardioRisk`;
  observeReveals($(`.view[data-view="${view}"]`));
  loaders[view]();
}
addEventListener("hashchange", route);

// ---------- home ----------
let homeDone = false;
async function loadHome() {
  if (homeDone) return; homeDone = true;
  const m = await getMetrics(), t = m.test.default_threshold;
  $("#heroModel").textContent = `${MODEL_NAMES[m.selected_model] || m.selected_model} · ${pct(t.accuracy)} test accuracy`;
  const b = $$("#heroStats b");
  countUp(b[0], t.accuracy * 100, (v) => v.toFixed(1) + "%");
  countUp(b[1], t.roc_auc, (v) => v.toFixed(3));
  countUp(b[2], t.recall_sensitivity * 100, (v) => v.toFixed(1) + "%");
  countUp(b[3], m.n_train + m.n_test, (v) => Math.round(v).toLocaleString());
  const rows = Object.entries(m.cv_comparison).sort((a, b) => b[1].accuracy[0] - a[1].accuracy[0]);
  const max = rows[0][1].accuracy[0];
  $("#homeCmp tbody").innerHTML = rows.map(([n, s]) => `
    <tr class="${n === m.selected_model ? "best" : ""}">
      <td>${MODEL_NAMES[n] || n}</td>
      <td class="mono">${pct(s.accuracy[0])}<span class="sd">± ${(s.accuracy[1] * 100).toFixed(1)}</span></td>
      <td class="mono">${s.roc_auc[0].toFixed(3)}</td>
      <td class="mono">${pct(s.recall[0])}</td>
      <td style="width:28%">${n === m.selected_model ? '<span class="tag">Selected</span>' : `<div class="bar"><i data-w="${(s.accuracy[0] / max) * 100}"></i></div>`}</td>
    </tr>`).join("");
  requestAnimationFrame(() => $$("#homeCmp .bar i").forEach((i) => (i.style.width = i.dataset.w + "%")));
}

// ---------- predict ----------
const seg = $(".seg");
seg.addEventListener("click", (e) => {
  const b = e.target.closest("button"); if (!b) return;
  $$("button", seg).forEach((x) => x.classList.toggle("on", x === b));
  seg.classList.toggle("right", b === seg.lastElementChild);
});
const EXAMPLE = { age: 63, sex: 1, cp: 4, trestbps: 145, chol: 233, fbs: 1, restecg: 2, thalach: 150, exang: 1, oldpeak: 2.3, slope: 3, ca: 2, thal: 7 };
$("#sample").addEventListener("click", () => {
  const f = $("#form");
  for (const [k, v] of Object.entries(EXAMPLE)) if (f.elements[k]) f.elements[k].value = v;
  $$("button", seg).forEach((x) => x.classList.toggle("on", Number(x.dataset.v) === EXAMPLE.sex));
  seg.classList.toggle("right", EXAMPLE.sex === 0);
  toast("High-risk example loaded");
});

const arc = $("#arc"); const LEN = arc.getTotalLength();
arc.style.strokeDasharray = LEN; arc.style.strokeDashoffset = LEN;

$("#form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target, btn = $("#submit");
  btn.disabled = true; btn.classList.add("loading"); $("#err").textContent = "";
  const body = { sex: Number($(".seg button.on").dataset.v) };
  for (const [k, v] of new FormData(form)) body[k] = v === "" ? null : Number(v);
  try {
    const r = await fetch("/api/predict", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const j = await r.json();
    if (!r.ok) throw new Error(Array.isArray(j.detail) ? j.detail.map((d) => `${LABELS[d.loc.at(-1)] || d.loc.at(-1)}: ${d.msg}`).join(" · ") : j.detail || r.statusText);
    render(j);
    historyDirty = true;
    if (innerWidth < 960) $("#result").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    $("#err").textContent = err.message;
    form.classList.remove("shake"); void form.offsetWidth; form.classList.add("shake");
  }
  btn.disabled = false; btn.classList.remove("loading");
});

function riskColor(p) { return p >= 0.7 ? css("--danger") : p >= 0.4 ? css("--warn") : css("--ok"); }
function render(res) {
  $("#empty").hidden = true;
  const out = $("#out"); out.hidden = false; out.style.animation = "none"; void out.offsetWidth; out.style.animation = "";
  const p = res.probability, color = riskColor(p);
  arc.style.stroke = color;
  arc.style.strokeDashoffset = LEN;
  requestAnimationFrame(() => requestAnimationFrame(() => (arc.style.strokeDashoffset = LEN * (1 - p))));
  const el = $("#pct"); el.style.color = color;
  countUp(el, p * 100, (v) => v.toFixed(1) + "%", 1100);
  const level = p >= 0.7 ? ["bad", "High risk · disease likely"] : p >= 0.4 ? ["", "Moderate risk"] : ["ok", "Low risk · disease unlikely"];
  $("#verdict").innerHTML = `<span class="tag ${level[0]}">${level[1]}</span>`;
  $("#meta").textContent = `${MODEL_NAMES[res.model] || res.model} · threshold ${res.threshold}`;
  const ex = res.explanation.slice(0, 10);
  draw("#shap", () => ({
    type: "bar",
    data: { labels: ex.map((d) => `${LABELS[d.feature]}  ${d.value ?? "?"}`),
      datasets: [{ data: ex.map((d) => d.contribution), backgroundColor: ex.map((d) => d.contribution > 0 ? css("--danger") : css("--ok")), borderRadius: 4, barThickness: 16 }] },
    options: { indexAxis: "y", maintainAspectRatio: false, plugins: { legend: { display: false },
        tooltip: { callbacks: { label: (c) => `${c.raw > 0 ? "+" : ""}${c.raw.toFixed(3)} log-odds` } } },
      scales: { x: { grid: grid(), border: { display: false } }, y: { grid: { display: false }, border: { display: false }, ticks: { color: css("--ink") } } } },
  }));
}

// ---------- performance ----------
let perfDone = false;
async function loadPerformance() {
  if (perfDone) return; perfDone = true;
  const m = await getMetrics(), t = m.test.default_threshold;
  $("#perfSub").textContent = `${MODEL_NAMES[m.selected_model]} · train ${m.n_train} / test ${m.n_test} · threshold 0.5 · the test set was never used for tuning`;
  const k = [["Accuracy", t.accuracy], ["ROC-AUC", t.roc_auc, 1], ["Sensitivity", t.recall_sensitivity], ["Specificity", t.specificity],
    ["Precision", t.precision], ["F1 score", t.f1, 1], ["Balanced accuracy", t.balanced_accuracy], ["PR-AUC", t.pr_auc, 1], ["MCC", t.mcc, 1], ["Brier (lower is better)", t.brier, 1]];
  $("#kpis").innerHTML = k.map(([n, v]) => `<div class="kpi card reveal"><b class="mono">–</b><span>${n}</span><div class="bar"><i data-w="${v * 100}"></i></div></div>`).join("");
  $$("#kpis .kpi").forEach((el, i) => {
    const [, v, raw] = k[i];
    countUp($("b", el), raw ? v : v * 100, raw ? (x) => x.toFixed(3) : (x) => x.toFixed(1) + "%");
  });
  observeReveals($("#kpis"));
  requestAnimationFrame(() => $$("#kpis .bar i").forEach((i) => (i.style.width = i.dataset.w + "%")));
  const c = t.confusion_matrix;
  $("#cm").innerHTML = `<div class="h"></div><div class="h">Predicted no</div><div class="h">Predicted yes</div>
    <div class="h">Actual no</div><div class="v ok" style="--d:0ms">${c.tn}</div><div class="v no" style="--d:80ms">${c.fp}</div>
    <div class="h">Actual yes</div><div class="v no" style="--d:160ms">${c.fn}</div><div class="v ok" style="--d:240ms">${c.tp}</div>`;
  const line = (xs, ys, extra = {}) => ({ data: xs.map((x, i) => ({ x, y: ys[i] })), borderColor: css("--accent"), backgroundColor: css("--accent-soft"), borderWidth: 2, pointRadius: 0, ...extra });
  const base = (x, y) => ({ maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: axes(x, y) });
  draw("#roc", () => ({ type: "line", data: { datasets: [line(m.curves.roc.fpr, m.curves.roc.tpr, { fill: "origin" }), diag()] }, options: base("False positive rate", "True positive rate") }));
  draw("#cal", () => ({ type: "line", data: { datasets: [line(m.curves.calibration.predicted, m.curves.calibration.observed, { pointRadius: 4, pointBackgroundColor: css("--surface"), pointBorderWidth: 2 }), diag()] }, options: base("Predicted probability", "Observed frequency") }));
  draw("#pr", () => ({ type: "line", data: { datasets: [line(m.curves.pr.recall, m.curves.pr.precision, { stepped: true, fill: "origin" })] }, options: base("Recall", "Precision") }));
  const imp = m.feature_importance.slice(0, 10);
  draw("#imp", () => ({ type: "bar", data: { labels: imp.map((d) => LABELS[d[0]] || d[0]),
      datasets: [{ data: imp.map((d) => d[1]), backgroundColor: imp.map((_, i) => css("--accent") + Math.round(255 * (1 - i * 0.07)).toString(16).padStart(2, "0")), borderRadius: 4, barThickness: 14 }] },
    options: { indexAxis: "y", maintainAspectRatio: false, plugins: { legend: { display: false } },
      scales: { x: { grid: grid(), border: { display: false } }, y: { grid: { display: false }, border: { display: false }, ticks: { color: css("--ink") } } } } }));
  const f = ([mu, sd]) => `${pct(mu)}<span class="sd">± ${(sd * 100).toFixed(1)}</span>`;
  $("#cmp tbody").innerHTML = Object.entries(m.cv_comparison).sort((a, b) => b[1].accuracy[0] - a[1].accuracy[0])
    .map(([n, s]) => `<tr class="${n === m.selected_model ? "best" : ""}"><td>${MODEL_NAMES[n] || n} ${n === m.selected_model ? '<span class="tag">Selected</span>' : ""}</td>
      <td class="mono">${f(s.accuracy)}</td><td class="mono">${f(s.roc_auc)}</td><td class="mono">${f(s.f1)}</td><td class="mono">${f(s.recall)}</td></tr>`).join("");
}

// ---------- data ----------
let dataDone = false;
async function loadData() {
  if (dataDone) return; dataDone = true;
  const d = await (await fetch("/static/eda/summary.json")).json();
  $("#dataSub").textContent = `Four hospital sites · ${d.rows} patients after cleaning · ${pct(d.positive_rate)} have heart disease`;
  $("#siteKpis").innerHTML = Object.entries(d.by_site).map(([s, v]) =>
    `<div class="kpi card reveal"><b class="mono">${v.rows}</b><span>${s}</span><div class="bar"><i data-w="${v.positive_rate * 100}"></i></div><span class="hint">${pct(v.positive_rate)} positive</span></div>`).join("");
  const titles = { "class_balance.png": "Class balance by site", "missingness.png": "Missing values by site", "distributions.png": "Distributions by outcome",
    "categorical_rates.png": "Disease rate by category", "correlation.png": "Correlation matrix" };
  $("#edaPlots").innerHTML = d.plots.map((p) =>
    `<div class="card eda reveal ${/distributions|categorical/.test(p) ? "wide" : ""}"><h3>${titles[p] || p}</h3><img src="/static/eda/${p}" alt="${titles[p] || p}" loading="lazy" /></div>`).join("");
  observeReveals($('.view[data-view="data"]'));
  requestAnimationFrame(() => $$("#siteKpis .bar i").forEach((i) => (i.style.width = i.dataset.w + "%")));
}

// ---------- history ----------
let historyDirty = true;
async function loadHistory() {
  if (!historyDirty) return; historyDirty = false;
  const tb = $("#hist tbody");
  tb.innerHTML = `<tr><td colspan="6"><div class="skeleton line"></div><div class="skeleton line"></div><div class="skeleton line"></div></td></tr>`;
  const rows = await (await fetch("/api/history")).json();
  tb.innerHTML = rows.length ? rows.map((r, i) => `<tr class="reveal" style="--d:${Math.min(i, 10) * 30}ms"><td>${new Date(r.created_at).toLocaleString()}</td><td class="mono">${r.inputs.age}</td>
    <td>${r.inputs.sex ? "Male" : "Female"}</td><td>${CP[r.inputs.cp]}</td><td class="mono">${pct(r.probability)}</td>
    <td><span class="tag ${r.label ? "bad" : "ok"}">${r.label ? "Likely" : "Unlikely"}</span></td></tr>`).join("")
    : `<tr><td colspan="6" class="hint" style="padding:28px 10px">No predictions yet. <a class="accent-ink" href="#/predict">Run one →</a></td></tr>`;
  requestAnimationFrame(() => $$("#hist tr.reveal").forEach((r) => r.classList.add("in")));
}

// ---------- boot ----------
chartDefaults();
const _toggle = $("#theme");
_toggle.addEventListener("click", () => setTimeout(chartDefaults, 200));
route();
