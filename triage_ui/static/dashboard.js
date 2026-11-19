const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const VULNS = ["sqli", "xss", "command_injection", "path_traversal"];
const EVASIONS = ["none", "encoding", "case_variation", "comment_injection", "whitespace_substitution"];
const VULN_NAMES = {sqli:"SQL injection",xss:"Cross-site scripting",command_injection:"Command injection",path_traversal:"Path traversal"};
const EVASION_NAMES = {none:"None",encoding:"Encoding",case_variation:"Case variation",comment_injection:"Comment injection",whitespace_substitution:"Whitespace substitution"};
let toastTimer;
let reviewItem = null;

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
}
function number(value, digits = 0) { return Number(value || 0).toLocaleString(undefined, {maximumFractionDigits:digits, minimumFractionDigits:digits}); }
function percent(value, digits = 1) { return `${(Number(value || 0) * 100).toFixed(digits)}%`; }
function notify(message, error = false) {
  const toast = $("#toast"); toast.textContent = message; toast.classList.toggle("error", error); toast.classList.add("show");
  clearTimeout(toastTimer); toastTimer = setTimeout(() => toast.classList.remove("show"), 3600);
}
async function api(url, options = {}) {
  const response = await fetch(url, {headers:{"Content-Type":"application/json", ...(options.headers || {})}, ...options});
  let data = null;
  try { data = await response.json(); } catch {}
  if (!response.ok) throw new Error(data?.detail || `Request failed (${response.status})`);
  return data;
}
function setState(id, state) {
  const node = document.getElementById(id); if (!node) return;
  node.classList.remove("is-good", "is-warn", "is-bad"); if (state) node.classList.add(`is-${state}`);
}
function switchView(name) {
  const view = $(`#view-${name}`); if (!view) return;
  $$(".view").forEach(el => el.classList.toggle("active", el === view));
  $$(".nav-link").forEach(el => el.classList.toggle("active", el.dataset.view === name));
  $("#current-section").textContent = view.dataset.title;
  history.replaceState(null, "", `#${name}`);
  if (name === "triage") loadTriage();
  if (name === "archive") loadArchive();
  if (name === "learning") loadLearning();
  if (name === "telemetry") loadTelemetry();
  if (name === "elites") loadElites();
}
function classTag(value) {
  const label = VULN_NAMES[value] || value || "Unknown class";
  return `<span class="class-tag class-${escapeHtml(value)}">${escapeHtml(label)}</span>`;
}
function requestSummary(item) {
  const ev = item.trial_result?.request_evidence;
  if (!ev) return item.genome?.injection_point || "Captured request";
  let path = "";
  try { path = new URL(ev.url).pathname; } catch { path = ev.url || ""; }
  return `${ev.method || "HTTP"} ${path}`;
}
function detectorCell(result) {
  return result?.detector_flagged
    ? `<span class="signal-yes">Flagged · ${number(result.detector_confidence, 2)}</span>`
    : `<span class="signal-no">Not flagged · ${number(result?.detector_confidence, 2)}</span>`;
}
function rowActions(item, compact = false) {
  const id = escapeHtml(item.id);
  const actions = `<button class="row-action" data-open="${id}">Inspect</button>`;
  if (item.status !== "pending") return actions + `<span class="state-tag">${escapeHtml(item.status)}</span>`;
  return actions + `<button class="row-action confirm" data-review="confirm" data-id="${id}" ${compact ? "" : "title='Confirm after reviewing evidence'"}>Confirm</button>` + (compact ? "" : `<button class="row-action" data-review="reject" data-id="${id}">Reject</button>`);
}

async function loadStatus() {
  const [status, learning] = await Promise.all([api("/api/status"), api("/api/learning/status")]);
  const co = status.coevolution, triage = status.triage, classes = learning.class_counts;
  $("#stat-generation").textContent = number(co.current_generation);
  $("#gen-secondary").textContent = number(co.current_generation);
  $("#stat-coverage").textContent = percent(co.archive_coverage);
  $("#stat-cells").textContent = `${number(co.archive_filled_cells)} / ${number(co.total_possible_cells)} behavioral cells`;
  $("#stat-qd").textContent = number(co.qd_score, 2);
  $("#stat-pending").textContent = number(triage.pending);
  $("#nav-pending").textContent = number(triage.pending);
  $("#stat-labeled").textContent = number(learning.labeled_unique_cases);
  $("#stat-balance").textContent = `${number(classes.benign)} benign · ${number(classes.malicious)} malicious`;
  $("#coverage-bar").style.width = percent(co.archive_coverage);
  $("#coverage-value").textContent = percent(co.archive_coverage);
  renderBandit(co.bandit_arm_weights || {});
  const target = status.dvwa_target.online;
  $("#dvwa-status").textContent = target ? "Responding on internal network" : "Not reachable from dashboard";
  setState("dvwa-dot", target ? "good" : "bad");
  const detector = status.blue_detector;
  $("#detector-status").textContent = detector.online ? (detector.has_model ? `Laya loaded · ${detector.current_model || "local checkpoint"}` : "Service online · model unavailable") : "Detector offline";
  setState("detector-dot", detector.online && detector.has_model ? "good" : "bad");
  const planner = status.strategy_planner;
  $("#planner-status").textContent = planner.bridge_reachable ? `${planner.model} · key configured` : "Bridge unavailable or unconfigured";
  setState("planner-dot", planner.bridge_reachable ? "good" : "warn");
  $("#network-status").textContent = status.network_scope || status.sandbox_network;
  setState("network-dot", "good");
  const online = target && detector.online && detector.has_model;
  $("#system-label").textContent = online ? "Lab ready" : "Lab needs attention";
  setState("system-dot", online ? "good" : "warn");
  $("#scope-indicator").classList.toggle("is-good", true);
  $("#last-updated").textContent = `Updated ${new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})}`;
  $("#evidence-total").textContent = number(learning.labeled_unique_cases);
  $("#benign-count").textContent = number(classes.benign);
  $("#malicious-count").textContent = number(classes.malicious);
  const total = Math.max(1, classes.benign + classes.malicious);
  $("#benign-bar").style.width = `${classes.benign / total * 100}%`;
  $("#malicious-bar").style.width = `${classes.malicious / total * 100}%`;
  $("#training-readiness").textContent = learning.ready_to_train ? "Both classes meet the minimum; evaluate on held-out states." : `Need ${Math.max(0, learning.minimum_per_class - classes.benign)} more benign and ${Math.max(0, learning.minimum_per_class - classes.malicious)} more malicious labels to meet the default gate.`;
}
function renderBandit(weights) {
  const entries = Object.entries(weights);
  if (!entries.length) { $("#bandit-bars").innerHTML = '<p class="quiet-text">No operator weights recorded yet.</p>'; return; }
  const max = Math.max(1, ...entries.map(([, value]) => Number(value) || 0));
  $("#bandit-bars").innerHTML = entries.map(([name, value]) => `<div class="bandit-item"><span>${escapeHtml(name.replaceAll("_", " "))}</span><span class="bandit-track"><i style="width:${Math.max(2,(Number(value)||0)/max*100)}%"></i></span><b>${number(value,2)}</b></div>`).join("");
}
function triageUrl(limitStatus = true) {
  const params = new URLSearchParams();
  const status = $("#filter-status") ? $("#filter-status").value : "confirmed";
  const vuln = $("#filter-vuln")?.value ?? "";
  const query = $("#filter-search")?.value.trim() ?? "";
  if (limitStatus && status) params.set("status", status);
  if (vuln) params.set("vuln_class", vuln);
  if (query) params.set("search", query);
  return `/api/triage?${params}`;
}
function triageRow(item, compact = false) {
  const result = item.trial_result || {};
  const compromised = result.target_compromised;
  if (compact) return `<tr><td><span class="finding-id">${escapeHtml(item.id.slice(0,8))}</span></td><td>${classTag(item.genome.vuln_class)}</td><td class="${compromised ? "signal-yes" : "signal-no"}">${compromised ? `Signal · ${number(result.compromise_confidence,2)}` : "No direct signal"}</td><td>${detectorCell(result)}</td><td>${escapeHtml(item.archive_cell_status || "—")}</td><td><div class="row-actions">${rowActions(item,true)}</div></td></tr>`;
  return `<tr><td><input class="item-check" type="checkbox" value="${escapeHtml(item.id)}" aria-label="Select finding ${escapeHtml(item.id.slice(0,8))}"></td><td><span class="finding-id">${escapeHtml(item.id.slice(0,8))}</span></td><td>${classTag(item.genome.vuln_class)}</td><td class="request-cell" title="${escapeHtml(requestSummary(item))}">${escapeHtml(requestSummary(item))}</td><td class="${compromised ? "signal-yes" : "signal-no"}">${compromised ? `Signal · ${number(result.compromise_confidence,2)}` : "No direct signal"}</td><td>${detectorCell(result)}</td><td>${escapeHtml(item.archive_cell_status || "—")}</td><td><div class="row-actions">${rowActions(item,false)}</div></td></tr>`;
}
async function loadTriage() {
  const items = await api(triageUrl());
  $("#triage-count").textContent = number(items.length);
  $("#triage-table").innerHTML = items.length ? items.map(item => triageRow(item)).join("") : '<tr><td colspan="8" class="empty-row">No findings match these filters.</td></tr>';
  $$("#triage-table .item-check").forEach(box => box.addEventListener("change", updateSelection));
}
async function loadOverviewQueue() {
  let items = await api("/api/triage?status=confirmed");
  if (!items || !items.length) {
    items = await api("/api/triage");
  }
  $("#overview-queue").innerHTML = items && items.length ? items.slice(0,6).map(item => triageRow(item,true)).join("") : '<tr><td colspan="6" class="empty-row">No findings recorded yet. Run a generation to discover candidates.</td></tr>';
}
function updateSelection() { const checks = $$("#triage-table .item-check"); $("#select-all").checked = checks.length > 0 && checks.every(c => c.checked); }
async function openFinding(id) {
  const item = await api(`/api/triage/${encodeURIComponent(id)}`); reviewItem = item;
  const g = item.genome, trial = item.trial_result, evidence = trial.request_evidence || {};
  const request = {method:evidence.method,url:evidence.url,params:evidence.params,body:evidence.body,response_status:evidence.response_status,response_excerpt:evidence.response_excerpt,latency_ms:evidence.latency_ms};
  const meta = `${item.id} · generation ${number(g.generation)} · ${g.operator_used || "unknown operator"} · ${item.status}`;
  $("#finding-detail").innerHTML = `<h2>${escapeHtml(VULN_NAMES[g.vuln_class] || g.vuln_class)} finding</h2><p class="finding-meta">${escapeHtml(meta)}</p><div class="finding-detail-grid"><section class="detail-block"><label>Rendered request candidate</label><pre>${escapeHtml(g.rendered_payload || "No candidate recorded")}</pre></section><section class="detail-block"><label>Mutation template</label><pre>${escapeHtml(g.payload_template || "No template recorded")}</pre></section><section class="detail-block"><label>Target verification</label><pre>${escapeHtml(JSON.stringify({target_compromised:trial.target_compromised,confidence:trial.compromise_confidence,signature:trial.response_signature},null,2))}</pre></section><section class="detail-block"><label>Laya detector</label><pre>${escapeHtml(JSON.stringify({flagged:trial.detector_flagged,confidence:trial.detector_confidence,rule:trial.detector_rule_fired},null,2))}</pre></section><section class="detail-block wide"><label>Captured HTTP evidence</label><pre>${escapeHtml(JSON.stringify(request,null,2))}</pre></section></div><div class="detail-actions"><input id="review-note" maxlength="500" placeholder="Optional reviewer note" value="${escapeHtml(item.reviewer_note || "")}"><button class="button button-primary" data-modal-review="confirm">Confirm</button><button class="button button-quiet" data-modal-review="reject">Reject</button><button class="button button-text" data-modal-review="duplicate">Duplicate</button></div>`;
  $("#finding-dialog").showModal();
}
async function review(id, action, note = "") {
  if (action === "confirm" && !window.confirm("Confirm this finding after reviewing its captured evidence?")) return;
  await api(`/api/triage/${encodeURIComponent(id)}`, {method:"POST",body:JSON.stringify({action,reviewer_note:note,reviewer_id:"local_dashboard_analyst"})});
  $("#finding-dialog").close(); notify(`Finding ${action === "duplicate" ? "marked duplicate" : `${action}ed`}.`); await refreshAll();
}
async function batchReview(action) {
  const ids = $$("#triage-table .item-check:checked").map(box => box.value);
  if (!ids.length) return notify("Select at least one finding first.", true);
  if (action === "confirm" && !window.confirm(`Confirm ${ids.length} selected finding(s) after review?`)) return;
  await api("/api/triage/batch",{method:"POST",body:JSON.stringify({ids,action,reviewer_id:"local_dashboard_analyst"})});
  notify(`${ids.length} finding(s) updated.`); await refreshAll();
}
async function loadArchive() {
  const data = await api("/api/archive/matrix");
  $("#archive-count").textContent = number(data.filled_count); $("#archive-total").textContent = number(data.total_possible_cells); $("#archive-qd").textContent = number(data.qd_score,2);
  const map = new Map();
  for (const cell of data.cells) { const key = `${cell.vuln_class}:${cell.evasion_technique}`; if (!map.has(key) || map.get(key).fitness < cell.fitness) map.set(key,cell); }
  let html = '<div class="archive-head">Class / transform</div>' + EVASIONS.map(ev => `<div class="archive-head">${escapeHtml(EVASION_NAMES[ev])}</div>`).join("");
  for (const vuln of VULNS) {
    html += `<div class="archive-row-label">${escapeHtml(VULN_NAMES[vuln])}</div>`;
    for (const ev of EVASIONS) {
      const cell = map.get(`${vuln}:${ev}`);
      if (!cell) html += '<div class="archive-cell is-empty" aria-label="Not explored"><strong>—</strong><small>Not reached</small></div>';
      else html += `<button class="archive-cell is-filled ${cell.fitness >= .7 ? "is-strong" : ""}" data-cell="${escapeHtml(vuln)}:${escapeHtml(ev)}"><strong>${number(cell.fitness,2)}</strong><small>${escapeHtml((cell.detector_outcome || "").replaceAll("_"," "))}</small></button>`;
    }
  }
  $("#archive-grid").innerHTML = html;
  $$("#archive-grid [data-cell]").forEach(button => button.addEventListener("click",() => {const [v,e]=button.dataset.cell.split(":"); const cell=map.get(`${v}:${e}`); notify(`${VULN_NAMES[v]} · ${EVASION_NAMES[e]} · fitness ${number(cell.fitness,2)} · ${cell.detector_outcome.replaceAll("_"," ")}`);}));
}
async function loadLearning() {
  const data = await api("/api/learning/status");
  const c = data.class_counts;
  $("#learning-benign").textContent = number(c.benign); $("#learning-malicious").textContent = number(c.malicious);
  $("#corpus-observations").textContent = number(data.observations); $("#corpus-labeled").textContent = number(data.labeled_unique_cases);
  $("#corpus-last-label").textContent = data.last_label_at ? new Date(data.last_label_at).toLocaleString() : "No labels recorded";
  $("#learning-gate-title").textContent = data.ready_to_train ? "Minimum label counts reached" : "More labeled observations needed";
  $("#learning-gate-copy").textContent = data.ready_to_train ? "Both classes meet the default threshold. Check the held-out split before training." : `Current set: ${c.benign} benign and ${c.malicious} malicious. The default gate is ${data.minimum_per_class} distinct states per class.`;
  $("#base-model-state").textContent = data.base_checkpoint_present ? "Available" : "Missing";
  $("#base-model-state").className = `state-tag ${data.base_checkpoint_present ? "ready" : "missing"}`;
  $("#candidate-model-state").textContent = data.candidate_checkpoint_present ? "Candidate exists" : "Not trained";
  $("#candidate-model-state").className = `state-tag ${data.candidate_checkpoint_present ? "ready" : "missing"}`;
  const sourceEntries = Object.entries(data.label_sources || {});
  $("#label-sources").innerHTML = sourceEntries.length ? sourceEntries.map(([source,count])=>`<span class="source-chip">${escapeHtml(source.replaceAll("_"," "))} · ${number(count)}</span>`).join("") : '<span class="quiet-text">No source-traced labels recorded.</span>';
}
async function loadTelemetry() {
  const data = await api("/api/metrics?limit=50");
  $("#metrics-table").innerHTML = data.length ? [...data].reverse().map(m=>`<tr><td>${escapeHtml(m.timestamp ? new Date(m.timestamp).toLocaleString() : "—")}</td><td>${number(m.generation)}</td><td>${percent(m.archive_coverage)}</td><td>${number(m.qd_score,2)}</td><td>${percent(m.blue_regression_pass_rate,0)}</td><td>${number(m.pending_triage_count)}</td></tr>`).join("") : '<tr><td colspan="6" class="empty-row">No snapshots recorded yet. Run a generation to start the log.</td></tr>';
  const chart = $("#coverage-chart");
  if (!data.length) { chart.innerHTML = '<p class="empty-row">No measured archive coverage yet.</p>'; return; }
  const points = data.slice(-30), maxGen = Math.max(1,...points.map(x=>Number(x.generation)||0));
  chart.innerHTML = points.map(item=>`<div class="chart-bar" style="height:${Math.max(3,Number(item.archive_coverage||0)*100)}%" title="Generation ${number(item.generation)} · ${percent(item.archive_coverage)}"><span>${number(item.generation) === number(maxGen) || points.length < 9 ? number(item.generation) : ""}</span></div>`).join("");
}
async function loadElites() {
  const data = await api("/api/hall-of-fame"); $("#elite-count").textContent = number(data.length);
  $("#elite-table").innerHTML = data.length ? data.map(item=>`<tr><td class="finding-id">${escapeHtml(item.id.slice(0,8))}</td><td>${escapeHtml(item.entry_type.replaceAll("_"," "))}</td><td>${number(item.retired_at_generation)}</td><td>${escapeHtml(item.confirmed_by || "—")}</td><td class="request-cell" title="${escapeHtml(item.blue_model_path || item.genome?.rendered_payload || "")}">${escapeHtml(item.blue_model_path || item.genome?.rendered_payload || "—")}</td></tr>`).join("") : '<tr><td colspan="5" class="empty-row">No archived elites or model snapshots yet.</td></tr>';
}
async function runAction(action) {
  const buttons = $$(`[data-action="${action}"]`); buttons.forEach(b=>b.disabled=true);
  try {
    let result;
    if (action === "step") result = await api("/api/orchestrator/step",{method:"POST"});
    if (action === "epoch") result = await api("/api/orchestrator/epoch",{method:"POST",body:JSON.stringify({generations:5})});
    if (action === "regression") result = await api("/api/learning/regression",{method:"POST"});
    if (action === "auto-triage") result = await api("/api/triage/auto",{method:"POST"});
    if (action === "regression") notify(`Regression recorded · blue ${percent(result.blue_regression_pass_rate)} · red ${percent(result.red_regression_pass_rate)}`);
    else if (action === "auto-triage") notify(`Auto-triage complete: ${result.confirmed} confirmed Red Elites (${result.red_elites_count} in Hall of Fame)`);
    else notify(action === "step" ? `Generation ${number(result.generation)} recorded (auto-triaged).` : `${number(result.generations_completed)} generations completed (auto-triaged).`);
    await refreshAll();
  } catch (error) { notify(error.message, true); }
  finally { buttons.forEach(b=>b.disabled=false); }
}
async function refreshAll() {
  try { await Promise.all([loadStatus(),loadOverviewQueue()]); }
  catch (error) { $("#system-label").textContent="Dashboard data unavailable"; setState("system-dot","bad"); notify(error.message,true); }
  const active = $(".view.active")?.id.replace("view-","");
  if (active === "triage") await loadTriage().catch(error=>notify(error.message,true));
  if (active === "learning") await loadLearning().catch(error=>notify(error.message,true));
  if (active === "archive") await loadArchive().catch(error=>notify(error.message,true));
  if (active === "telemetry") await loadTelemetry().catch(error=>notify(error.message,true));
  if (active === "elites") await loadElites().catch(error=>notify(error.message,true));
}

document.addEventListener("click", async event => {
  const nav = event.target.closest("[data-view]"); if (nav) return switchView(nav.dataset.view);
  const go = event.target.closest("[data-go]"); if (go) return switchView(go.dataset.go);
  const open = event.target.closest("[data-open]"); if (open) { try { await openFinding(open.dataset.open); } catch (e) { notify(e.message,true); } return; }
  const reviewButton = event.target.closest("[data-review]"); if (reviewButton) { try { await review(reviewButton.dataset.id,reviewButton.dataset.review); } catch (e) { notify(e.message,true); } return; }
  const modalReview = event.target.closest("[data-modal-review]"); if (modalReview && reviewItem) { try { await review(reviewItem.id,modalReview.dataset.modalReview,$("#review-note")?.value || ""); } catch (e) { notify(e.message,true); } return; }
  const action = event.target.closest("[data-action]"); if (action && ["step","epoch","regression","auto-triage"].includes(action.dataset.action)) { await runAction(action.dataset.action); return; }
  if (action?.dataset.action === "batch-confirm" || action?.dataset.action === "batch-reject") { try { await batchReview(action.dataset.action.endsWith("confirm") ? "confirm" : "reject"); } catch (e) { notify(e.message,true); } }
});
$("#refresh-button").addEventListener("click",refreshAll); $("#footer-refresh").addEventListener("click",refreshAll);
$("#filter-status").addEventListener("change",()=>loadTriage().catch(e=>notify(e.message,true)));
$("#filter-vuln").addEventListener("change",()=>loadTriage().catch(e=>notify(e.message,true)));
let searchTimer; $("#filter-search").addEventListener("input",()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>loadTriage().catch(e=>notify(e.message,true)),180);});
$("#select-all").addEventListener("change",event=>$$("#triage-table .item-check").forEach(box=>box.checked=event.target.checked));
$("#finding-dialog").addEventListener("click",event=>{if(event.target===$("#finding-dialog")) $("#finding-dialog").close();});
const initial = location.hash.slice(1); if (initial && $(`#view-${initial}`)) switchView(initial);
refreshAll(); setInterval(()=>{if(!document.hidden)refreshAll();},20000);
