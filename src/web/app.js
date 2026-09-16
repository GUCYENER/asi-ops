let DATA = null;

const STATUSES = ["Acik", "Devam", "Kapali"];
const OWNERS = ["Ag Ekibi", "DBA Nobetcisi", "Uygulama Nobetcisi", "Entegrasyon Nobetcisi",
                "Batch Nobetcisi", "Nobetci Muhendis"];

function esc(value) {
  return String(value == null ? "" : value)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

async function load() {
  const response = await fetch("/api/data");
  DATA = await response.json();
  renderBadges();
  renderCards();
  renderNoise();
  renderUnclear();
  renderMetrics();
}

function renderBadges() {
  const m = DATA.metrics;
  document.getElementById("badges").innerHTML = [
    ["" + m.total_alarms, "alarm işlendi"],
    ["" + m.event_count, "olay kartı"],
    ["%" + (m.reduction_ratio * 100).toFixed(2), "indirgeme"],
    ["" + m.noise_count, "gürültü elendi"],
    ["" + m.accounted + "/" + m.total_alarms, "hesap verildi"],
  ].map(([big, label]) =>
    `<div class="badge"><b>${esc(big)}</b><span>${esc(label)}</span></div>`
  ).join("");
}

function renderCards() {
  document.getElementById("cards").innerHTML = DATA.events.map(cardHtml).join("");
  document.querySelectorAll(".card-head").forEach(head => {
    head.addEventListener("click", () => head.parentElement.classList.toggle("open"));
  });
  document.querySelectorAll("select[data-field]").forEach(select => {
    select.addEventListener("change", onActionChange);
    select.addEventListener("click", event => event.stopPropagation());
  });
  document.querySelectorAll("button.act[data-explain]").forEach(button => {
    button.addEventListener("click", onExplain);
  });
  document.querySelectorAll("button.statebtn").forEach(button => {
    button.addEventListener("click", onStatusClick);
  });
}

async function onStatusClick(event) {
  event.stopPropagation();
  const button = event.target;
  const id = button.dataset.id;
  const status = button.dataset.status;
  const response = await fetch("/api/actions/" + id, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  const updated = await response.json();
  const card = DATA.events.find(c => c.id === id);
  card.status = updated.status;
  document.querySelectorAll(`button.statebtn[data-id="${id}"]`).forEach(b => {
    b.classList.toggle("on", b.dataset.status === updated.status);
  });
  const pill = document.querySelector(`#card-${id} .card-title .pill[data-role="status"]`);
  if (pill) {
    pill.textContent = updated.status;
    pill.className = "pill status-" + updated.status;
    pill.dataset.role = "status";
  }
}

function cardHtml(card) {
  const counter = card.counter_hypotheses && card.counter_hypotheses[0];
  const narrative = card.narrative;
  return `
<article class="card" id="card-${esc(card.id)}">
  <div class="card-head">
    <div class="sev ${esc(card.severity_label)}"></div>
    <div class="card-main">
      <div class="card-title">
        <h3>#${card.rank} ${esc(card.title)}</h3>
        <span class="pill ${esc(card.severity_label)}">${esc(card.severity_label)}</span>
        <span class="pill">güven ${card.confidence.toFixed(2)}</span>
        <span class="pill status-${esc(card.status)}" data-role="status">${esc(card.status)}</span>
      </div>
      <div class="card-meta">
        <span><b>${card.alarm_count}</b> alarm</span>
        <span><b>${card.services.length}</b> servis</span>
        <span>${esc(card.time_start)} – ${esc(card.time_end)}</span>
        <span>${esc(card.racks.join(", "))}</span>
      </div>
      <div class="root">Kök neden hipotezi: <span>${esc(card.root_cause_hypothesis)}</span></div>
    </div>
    <div class="chev">⌄</div>
  </div>
  <div class="card-body">
    <div class="split">
      <div class="split-main">
        <div class="block">
          <h4>Kanıtlar</h4>
          <ul class="evidence">
            ${(card.evidence || [card.why]).map(e => `<li>${esc(e)}</li>`).join("")}
          </ul>
        </div>
      </div>
      <div class="split-side">
        <div class="conf-box">
          <span class="conf-label">Kök neden güveni</span>
          <b class="conf-value">%${Math.round(card.confidence * 100)}</b>
          <span class="conf-note">kanıt gücüne dayalı, kalibre edilmemiş</span>
        </div>
        ${counter ? `<div class="alt-box">
          <span class="conf-label">Alternatif hipotez</span>
          <b class="alt-value">%${Math.round(counter.confidence * 100)}</b>
          <span class="conf-note">${esc(counter.text)}</span>
        </div>` : ""}
      </div>
    </div>
    <div class="block">
      <h4>Çekirdek sinyaller</h4>
      <div class="tags">${card.signals.map(s => `<span class="tag">${esc(s)}</span>`).join("")}</div>
    </div>
    <div class="block">
      <h4>Etkilenen servisler (${card.services.length})</h4>
      <div class="tags">${card.services.map(s => `<span class="tag">${esc(s)}</span>`).join("")}</div>
    </div>
    <div class="block">
      <h4>Önerilen ilk aksiyon</h4>
      <div class="action-text">${esc(card.suggested_action)}</div>
      <div class="actions">
        <label>Sahip:
          <select data-field="owner" data-id="${esc(card.id)}">
            ${OWNERS.map(o => `<option ${o === card.owner ? "selected" : ""}>${esc(o)}</option>`).join("")}
          </select>
        </label>
        ${STATUSES.map(s => `<button class="statebtn ${s === card.status ? "on" : ""}"
          data-status="${esc(s)}" data-id="${esc(card.id)}">${esc(s.toUpperCase())}</button>`).join("")}
        <button class="act" data-explain="${esc(card.id)}">AI ile anlat</button>
      </div>
    </div>
    <div class="block" id="narrative-${esc(card.id)}">
      ${narrative ? `<h4>AI anlatısı (${esc(narrative.source)})</h4>
        <div class="narrative">${esc(narrative.text)}</div>` : ""}
    </div>
    <div class="block">
      <h4>Bu olaya bağlanan alarmlar (${card.alarms.length})</h4>
      <div class="scroll"><table>
        <thead><tr><th>Saat</th><th>Alarm</th><th>Servis</th><th>Host</th><th>Tip</th><th>Sev</th><th>Rol</th><th>Bağlanma gerekçesi</th></tr></thead>
        <tbody>${card.alarms.map(a => `<tr>
          <td class="mono">${esc(a.time)}</td>
          <td class="mono">${esc(a.alarm_id)}</td>
          <td>${esc(a.service)}</td>
          <td class="mono">${esc(a.host)}</td>
          <td>${esc(a.type)}</td>
          <td class="mono">${a.severity}</td>
          <td class="alarm-row-${esc(a.role)}">${esc(a.role)}</td>
          <td class="reason">${esc((a.link_reasons || []).join(" · "))}</td>
        </tr>`).join("")}</tbody>
      </table></div>
    </div>
  </div>
</article>`;
}

async function onActionChange(event) {
  const select = event.target;
  const id = select.dataset.id;
  const body = {};
  body[select.dataset.field] = select.value;
  const response = await fetch("/api/actions/" + id, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const updated = await response.json();
  const card = DATA.events.find(c => c.id === id);
  card.owner = updated.owner;
  card.status = updated.status;
  const pill = document.querySelector(`#card-${id} .card-title .pill.status-Acik,
    #card-${id} .card-title .pill.status-Devam, #card-${id} .card-title .pill.status-Kapali`);
  if (pill) {
    pill.textContent = updated.status;
    pill.className = "pill status-" + updated.status;
  }
}

async function onExplain(event) {
  const button = event.target;
  const id = button.dataset.explain;
  button.disabled = true;
  button.textContent = "Üretiliyor...";
  try {
    const response = await fetch("/api/explain/" + id);
    const data = await response.json();
    const target = document.getElementById("narrative-" + id);
    target.innerHTML = `<h4>AI anlatısı (${esc(data.source)})</h4>
      <div class="narrative">${esc(data.text)}</div>`;
    const card = DATA.events.find(c => c.id === id);
    card.narrative = data;
  } finally {
    button.disabled = false;
    button.textContent = "AI ile anlat";
  }
}

function rowsHtml(rows) {
  return `<div class="scroll"><table>
    <thead><tr><th>Saat</th><th>Alarm</th><th>Servis</th><th>Tip</th><th>Sev</th><th>Mesaj</th><th>Gerekçe</th></tr></thead>
    <tbody>${rows.map(r => `<tr>
      <td class="mono">${esc(r.time)}</td>
      <td class="mono">${esc(r.alarm_id)}</td>
      <td>${esc(r.service)}</td>
      <td>${esc(r.type)}</td>
      <td class="mono">${r.severity}</td>
      <td>${esc(r.message)}</td>
      <td class="reason">${esc(r.reason)}</td>
    </tr>`).join("")}</tbody></table></div>`;
}

function renderNoise() {
  const render = (filter) => {
    const term = (filter || "").toLowerCase();
    const rows = DATA.noise.filter(r => !term ||
      (r.service + r.type + r.reason + r.message).toLowerCase().includes(term));
    document.getElementById("noise-table").innerHTML =
      `<p class="reason">${rows.length} kayıt gösteriliyor.</p>` + rowsHtml(rows.slice(0, 400)) +
      (rows.length > 400 ? `<p class="reason">İlk 400 kayıt gösterildi.</p>` : "");
  };
  render("");
  document.getElementById("noise-filter").addEventListener("input", e => render(e.target.value));
}

function renderUnclear() {
  document.getElementById("unclear-table").innerHTML =
    `<p class="reason">${DATA.unclear.length} kayıt.</p>` + rowsHtml(DATA.unclear.slice(0, 400));
}

function renderMetrics() {
  const m = DATA.metrics;
  const rows = [
    ["İşlenen alarm", `${m.processed_alarms} / ${m.total_alarms}`, "Tüm veri işlendi (örnekleme yok)"],
    ["Olay kartı", m.event_count, "Üst sınır 15"],
    ["İndirgeme oranı", "%" + (m.reduction_ratio * 100).toFixed(2), "1 − kart / toplam alarm"],
    ["Olaylara bağlanan alarm", m.alarms_in_events, "Kanıt skoru eşiğini geçenler"],
    ["Gürültü", m.noise_count, "Gerekçesiyle elenen"],
    ["Belirsiz", m.unclear_count, "Gürültüye atılmadı, ayrı tutuldu"],
    ["Hesap verilen toplam", `${m.accounted} / ${m.total_alarms}`, "Kayıp veya çift sayım yok"],
    ["Naif yöntem karşılaştırması", `${m.naive_card_count} kart`, "10dk pencere × servis bazlı gruplama"],
    ["Zaman aralığı", m.time_window, "Gözlem penceresi"],
  ];
  const profile = DATA.type_profile.map(p => `<tr>
    <td>${esc(p.type)}</td>
    <td class="mono">${p.ratio.toFixed(1)}x</td>
    <td class="mono">${p.peak}</td>
    <td class="mono">${p.median}</td>
    <td class="mono">${p.total}</td>
    <td class="${p.label === "sinyal" ? "sig" : "noi"}">${esc(p.label)}</td>
  </tr>`).join("");

  document.getElementById("metrics-body").innerHTML = `
    <table>${rows.map(([k, v, note]) => `<tr>
      <td><b>${esc(k)}</b></td><td class="mono">${esc(v)}</td><td class="reason">${esc(note)}</td>
    </tr>`).join("")}</table>
    <div class="block" style="margin-top:26px">
      <h4>Alarm tipi zamansal yoğunlaşma profili — gürültü ayrımının objektif dayanağı</h4>
      <p class="reason">Yoğunlaşma = tepe 10dk penceresi / medyan 10dk penceresi.
      Eşik elle ayarlanmadı; veriden türetildi. ≥4.0 sinyal, &lt;3.0 gürültü.</p>
      <div class="scroll"><table>
        <thead><tr><th>Alarm tipi</th><th>Yoğunlaşma</th><th>Tepe</th><th>Medyan</th><th>Toplam</th><th>Sınıf</th></tr></thead>
        <tbody>${profile}</tbody>
      </table></div>
    </div>`;
}

document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById("panel-" + tab.dataset.tab).classList.add("active");
  });
});

load();
