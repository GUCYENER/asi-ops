"use strict";
const $ = (id) => document.getElementById(id);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const num = (v) => Number(v).toLocaleString("tr-TR");
const time = (v) => String(v).slice(11, 19);
const shortTime = (v) => String(v).slice(11, 16);
const statuses = {open:"Açık", investigating:"İnceleniyor", resolved:"Çözüldü kaydı"};
const decisions = {incident:"Olaya bağlı", noise:"Gürültü adayı", uncertain:"Belirsiz"};
let report, selected, tab = "incidents", offset = 0, total = 0, searchTimer, requestSerial = 0, toastTimer;
const PAGE = 50;
const allCards = () => [...report.incidents, ...(report.review_candidates || [])];

async function api(path, body) {
  const response = await fetch(path, body === undefined ? {} : {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "İstek tamamlanamadı.");
  return data;
}
function notify(text, error = false) {
  const el = $("toast"); el.textContent = text; el.className = "toast" + (error ? " error" : ""); el.hidden = false;
  clearTimeout(toastTimer); toastTimer = setTimeout(() => el.hidden = true, 5500);
}
async function load() {
  $("refresh").disabled = true;
  try {
    report = await api("/api/report");
    if (!allCards().some(i => i.id === selected)) selected = allCards()[0]?.id;
    $("error").hidden = true; $("loading").hidden = true; $("overview").hidden = false;
    renderOverview(); renderList(); renderDetail(); renderMetrics();
    if (["noise","uncertain","all"].includes(tab)) await loadAlarms();
  } catch (error) { $("loading").hidden = true; $("error").hidden = false; $("error").textContent = "Veriler alınamadı. " + error.message; }
  finally { $("refresh").disabled = false; }
}
function renderOverview() {
  const s = report.summary;
  $("window").textContent = `${s.start.slice(0,10)} · ${shortTime(s.start)}–${shortTime(s.end)} · ${s.service_count} servis · ${s.host_count} host`;
  $("mode").textContent = report.narrative.mode === "template" ? "Deterministik analiz · API gerektirmez" : "Deterministik analiz + isteğe bağlı AI anlatı";
  const stats = [
    ["İŞLENEN ALARM",num(s.processed_count),`<em>%${s.coverage*100} kapsam</em> · ${num(s.input_count)} kayıt` ,"▥",false],
    ["OLAY ADAYI",num(s.incident_count),`${num(s.assigned_count)} alarm bağlı · +${s.review_candidate_count} inceleme kartı`,"◈",true],
    ["GÜRÜLTÜ ADAYI",num(s.noise_count),"Gerekçesiyle korundu · silinmedi","≈",false],
    ["BELİRSİZ KAYIT",num(s.uncertain_count),"İnsan incelemesi için ayrıldı","◇",false]
  ];
  $("stats").innerHTML = stats.map(([label,value,note,icon,highlight]) => `<div class="stat ${highlight?"highlight":""}"><div class="stat-label">${label}<span class="stat-icon">${icon}</span></div><div class="stat-value">${value}</div><div class="stat-note">${note}</div></div>`).join("");
  $("incident-count").textContent=`${s.incident_count} + ${s.review_candidate_count}`; $("noise-count").textContent=num(s.noise_count); $("uncertain-count").textContent=num(s.uncertain_count);
  $("coverage-value").textContent = "%" + s.coverage * 100;
  const rows = report.timeline, width=520, step=width/rows.length, max=Math.max(...rows.map(r=>r.total),1);
  const bars=rows.map((r,i)=>{let y=73;const segments=["noise","uncertain","incident"].map(k=>{const h=r[k]/max*66;y-=h;return `<rect class="chart-${k}" x="${i*step+4}" y="${y}" width="${Math.max(3,step-9)}" height="${h}" rx="1"><title>${esc(shortTime(r.time))} · ${decisions[k]}: ${r[k]}</title></rect>`;}).join(""); return segments+(i%3===0 || i===rows.length-1?`<text x="${i*step+4}" y="92" class="chart-label">${esc(shortTime(r.time))}</text>`:"");}).join("");
  $("timeline").innerHTML=`<svg viewBox="0 0 540 100" role="img" aria-label="10 dakikalık dilimlerde alarm karar dağılımı">${bars}</svg>`;
  renderGantt();
  if (!s.card_limit_pass) {$("error").hidden=false;$("error").textContent="Kabul kontrolü: olay kartı sayısı 1–15 aralığında değil. Olaylar zorla birleştirilmedi.";}
}

function renderGantt() {
  const host = $("gantt");
  if (!host) return;
  const wrap = $("gantt-wrap"); if (wrap) wrap.hidden = false;
  const s = report.summary;
  const t0 = new Date(s.start).getTime(), span = Math.max(new Date(s.end).getTime() - t0, 1);
  const pos = iso => ((new Date(iso).getTime() - t0) / span);
  const kinds = {network:"Ağ", storage:"Depolama", memory:"Bellek", external:"Dış servis", batch:"Batch", unresolved:"Belirsiz kök"};
  const LABEL = 150, TRACK = 830, ROW = 34, PAD = 8;
  const rows = report.incidents;
  const height = rows.length * ROW + 34;

  const bars = rows.map((i, idx) => {
    const y = idx * ROW + PAD;
    const x = LABEL + pos(i.start) * TRACK;
    const w = Math.max(pos(i.end) * TRACK - pos(i.start) * TRACK, 3);
    const label = `${num(i.alarm_count)} alarm · ${shortTime(i.start)}–${shortTime(i.end)}`;
    const inside = w > 150;
    return `<g>
      <text x="0" y="${y + 11}" class="gt-svg-name">${esc(kinds[i.kind] || i.kind)}</text>
      <text x="0" y="${y + 22}" class="gt-svg-scope">${esc(i.root.scope)}</text>
      <rect x="${LABEL}" y="${y - 2}" width="${TRACK}" height="26" rx="6" class="gt-svg-track"></rect>
      <rect x="${x}" y="${y - 2}" width="${w}" height="26" rx="6" class="gt-k-${esc(i.kind)}"><title>${esc(i.title)}</title></rect>
      <text x="${inside ? x + 9 : x + w + 8}" y="${y + 15}" class="${inside ? "gt-svg-in" : "gt-svg-out"}">${esc(label)}</text>
    </g>`;
  }).join("");

  const ticks = Array.from({length: 7}, (_, k) => {
    const at = new Date(t0 + span * k / 6), x = LABEL + (k / 6) * TRACK;
    const hhmm = String(at.getHours()).padStart(2, "0") + ":" + String(at.getMinutes()).padStart(2, "0");
    return `<line x1="${x}" y1="${PAD - 4}" x2="${x}" y2="${rows.length * ROW + 2}" class="gt-svg-grid"></line>
      <text x="${x}" y="${rows.length * ROW + 18}" class="gt-svg-tick">${hhmm}</text>`;
  }).join("");

  host.innerHTML = `<svg viewBox="0 0 1000 ${height}" role="img" aria-label="Olayların zaman içindeki konumu">${ticks}${bars}</svg>
    <p class="gt-note"><strong>Olaylar zamanda iç içe geçiyor.</strong> Bellek olayı (01:35–03:00) ağ, depolama ve dış servis pencereleriyle çakışıyor — bu yüzden "anomali penceresi bul, içindekileri o olaya ata" yaklaşımı yanlış sonuç verir. Atama alarm seviyesinde, kanıt puanıyla yapılır.</p>`;
}
function renderList() {
  const card = i => `<button class="incident-card ${i.id===selected?"selected":""}" data-incident="${esc(i.id)}" data-card-type="${i.card_type||"incident"}" aria-pressed="${i.id===selected}"><div class="card-top"><span class="badge ${i.card_type==="review"?"warn":"priority"}">${i.card_type==="review"?"Düşük kanıt":esc(i.priority.level)}</span><span>${esc(i.id)}</span><span class="time">${shortTime(i.start)}–${shortTime(i.end)}</span></div><div class="card-title">${esc(i.root.hypothesis)}</div><div class="card-scope">${esc(i.root.scope)}</div><div class="card-bottom"><span><strong>${i.alarm_count}</strong> ${i.card_type==="review"?"belirsiz kayıt":"alarm"} · <strong>${i.services.length}</strong> servis</span><span class="badge ${i.action.status==="resolved"?"good":"neutral"}">${statuses[i.action.status]}</span></div></button>`;
  $("incident-list").innerHTML=report.incidents.map(card).join("")+(report.review_candidates?.length?`<div class="review-heading"><h3>İnceleme adayları · ${report.review_candidates.length}</h3><p>Yeni bağımsız olay oldukları doğrulanmadı. Bu kayıtlar belirsiz sayacında kalır.</p></div>`+report.review_candidates.map(card).join(""):"") || '<div class="empty">Güçlü olay adayı bulunamadı. Belirsiz kayıtları inceleyin.</div>';
  document.querySelectorAll("[data-incident]").forEach(b=>b.addEventListener("click",()=>{selected=b.dataset.incident;renderList();renderDetail();}));
}
function renderDetail() {
  const i=allCards().find(i=>i.id===selected);
  if (!i) {$("incident-detail").innerHTML='<div class="empty">İncelenecek olay seçin.</div>';return;}
  const badge=i.confidence.level==="yüksek"?"good":"warn";
  const review=i.card_type==="review";
  $("incident-detail").innerHTML=`<div class="detail-head"><div class="detail-kicker"><span class="eyebrow">${review?"İNCELEME ADAYI":i.priority.level==="P1"?"KRİTİK OLAY HİPOTEZİ":"OLAY HİPOTEZİ"} <span class="subtle"> / ${esc(i.id)}</span></span><span class="badge ${badge}" title="${esc(i.confidence.meaning)}">Kanıt: ${esc(i.confidence.level)}</span></div><h2>${esc(i.root.scope)}<br><span class="detail-title-secondary">${esc(i.root.hypothesis)}</span></h2><div class="detail-sub">${esc(i.start.slice(0,10))} · ${time(i.start)} → ${time(i.end)} · ilk/son ilişkili alarm</div><div class="detail-meta executive-meta"><div>${review?"Belirsiz kayıt":"İlişkili alarm"}<strong>${num(i.alarm_count)}</strong></div><div>${review?"Gözlenen host":"Doğrudan kök sinyali"}<strong>${review?i.hosts.length:i.direct_hosts?.length||0} host</strong></div><div>Gözlenen etki<strong>${i.services.length} servis</strong></div></div><div class="confidence-note">Kanıt düzeyi ${esc(i.confidence.level)} · Kalibre edilmiş kök neden olasılığı değildir.</div></div>
  <div class="detail-body">
  <div class="ai-strip"><div class="ai-strip-head"><span class="eyebrow">${report.narrative.mode==="optional_llm"?"AI ANLATISI":"KANIT ÖZETİ"}</span><button class="primary small" id="narrative">${report.narrative.mode==="optional_llm"?"AI ile özetle":"Kanıt özetini göster"}</button></div><p class="ai-strip-hint">Karar deterministik motordan gelir; model yalnızca hesaplanmış kanıtı anlatıya çevirir ve kanıt kimlikleri doğrulanır.</p><div id="narrative-result" hidden></div></div>
  ${review?`<div class="notice">Düşük kanıtlı inceleme adayı. ${esc(i.explanation)}${i.linked_incident_ids.length?`<br>Aidiyeti araştırılan olaylar: ${i.linked_incident_ids.map(esc).join(", ")}`:""}${Object.keys(i.message_targets||{}).length?`<br>Mesaj hedefleri: ${esc(JSON.stringify(i.message_targets))}`:""}</div>`:`<details class="sec" data-sec="evidence" open><summary><span class="number">01</span> KANIT ÖZETİ <span class="sec-hint">${(i.evidence_checks||[]).length} kanıt</span></summary><ul class="evidence-checks">${(i.evidence_checks||[]).map(c=>`<li><span aria-hidden="true">✓</span><div>${esc(c.text)}</div></li>`).join("")}</ul></details>`}
  ${i.dependency_evidence?.length?`<div class="dns-note"><strong>Hedef bağlantı kanıtı · ${esc(i.dependency_evidence[0].target)}</strong><p>${esc(i.dependency_evidence[0].interpretation)}</p></div>`:""}
  <div class="first-action"><div><div class="eyebrow">ÖNERİLEN İLK AKSİYON</div><p>${esc(i.action.recommendation)}</p></div><button class="secondary" id="jump-action">Aksiyona geç ↓</button></div>
  <details class="sec" data-sec="impact"><summary><span class="number">02</span> SERVİS ETKİSİ <span class="sec-hint">${i.services.length} servis</span></summary><div class="chips impact-chips">${i.services.map(service=>`<span class="chip">${esc(service)}</span>`).join("")}</div><p class="subtle footprint-note">İlişkili alarm bulunan toplam host: ${i.hosts.length}. ${review?"Kök host henüz belirlenmedi.":"Doğrudan kök sinyali veren host'lar yukarıda ayrıca sayıldı."}</p></details>
  <details class="sec" data-sec="alt"><summary><span class="number">02a</span> NEDEN BAŞKA AÇIKLAMA DEĞİL <span class="sec-hint">${i.alternatives.length} alternatif değerlendirildi</span></summary><p class="alt-intro">Aşağıdaki açıklama da mümkündü. Kanıtlar bu hipotezi neden daha az destekliyor ve bunu kesinleştirmek için ne ölçülmeli:</p><div class="counter">${i.alternatives.map(a=>`<strong>Değerlendirilen alternatif · ${esc(a.hypothesis)}</strong><p>${esc(a.comparison)}</p><small>Kesinleştirmek için: ${esc(a.next_check)}</small>`).join("")}</div></details>
  ${i.similar_incidents&&i.similar_incidents.length?`<details class="sec" data-sec="history"><summary><span class="number">02b</span> BENZER GEÇMİŞ OLAYLAR <span class="synth-tag">örnek arşiv · sentetik</span> <span class="sec-hint">%${Math.round(i.similar_incidents[0].similarity*100)} en yakın</span></summary>${i.similar_incidents.map(s=>`<div class="hist-card"><div class="hist-top"><strong>${esc(s.incident_id)}</strong> · ${esc(s.title)} <span class="hist-sim">%${Math.round(s.similarity*100)} benzer</span> <span class="hist-when">${esc(s.date)}</span></div><div class="hist-calc">alarm tipi örtüşmesi ${s.breakdown.alarm_tipi_ortusmesi} · servis örtüşmesi ${s.breakdown.servis_ortusmesi} · kategori eşleşmesi ${s.breakdown.kategori_eslesmesi}${s.shared_alarm_types.length?` · ortak tipler: ${esc(s.shared_alarm_types.join(", "))}`:""}</div><p class="hist-fix"><strong>O zaman ne işe yaradı:</strong> ${esc(s.resolution_action)} <span class="hist-mttr">${s.mttr_minutes} dk · ${esc(s.action_owner)}</span></p>${s.lessons_learned?`<p class="hist-lesson">${esc(s.lessons_learned)}</p>`:""}</div>`).join("")}<p class="subtle">Benzerlik bu uygulamada hesaplanır (0.45×alarm tipi + 0.35×servis + 0.20×kategori); arşivdeki hazır skor alanı kullanılmaz.</p></details>`:""}
  <details class="sec" data-sec="action" open id="action-panel"><summary><span class="number">03</span> SORUMLU VE DURUM <span class="sec-hint">${statuses[i.action.status]}</span></summary><div class="action-panel"><div class="status-now">Şu anki durum: <span class="status-chip s-${esc(i.action.status)}">${statuses[i.action.status]}</span> <span class="subtle">· sorumlu: ${esc(i.action.owner)}</span></div><div class="action-shortcuts"><button class="stepbtn" id="assign-owner" title="Sorumlu alanına odaklan">Sorumluyu değiştir</button><button class="stepbtn ${i.action.status==="investigating"?"current":""}" data-action-status="investigating" ${i.action.status==="investigating"?"disabled":""} title="Durumu İnceleniyor yap">${i.action.status==="investigating"?"● Şu an inceleniyor":"→ İncelemeye al"}</button><button class="stepbtn ${i.action.status==="resolved"?"current":""}" data-action-status="resolved" ${i.action.status==="resolved"?"disabled":""} title="Durumu Çözüldü yap; doğrulama notu zorunlu">${i.action.status==="resolved"?"● Çözüldü olarak kayıtlı":"✓ Çözüldü olarak kaydet"}</button></div><p class="alt-intro">Butonlar durumu doldurur; kaydı tamamlamak için <strong>Kaydet</strong>'e basın. Çözüldü kaydı doğrulama notu ister.</p><form id="action-form" class="action-form compact"><label>Sorumlu rol<input id="owner" required maxlength="120" value="${esc(i.action.owner)}"></label><label>Durum<select id="status">${Object.entries(statuses).map(([key,label])=>`<option value="${key}" ${key===i.action.status?"selected":""}>${label}</option>`).join("")}</select></label><label class="full">Doğrulama notu <span class="subtle">(çözüldü kaydı için zorunlu — insan onayı)</span><textarea id="action-note" maxlength="1000" rows="2" placeholder="Hangi kontrolü yaptınız?"></textarea></label><div class="form-footer full"><small>Sistem yalnızca <strong>öneri</strong> üretir; kaydı insan onaylar.</small><button class="primary" type="submit" id="save-action">Kaydet →</button></div></form><div id="action-error" class="notice error" role="alert" hidden></div></div></details>
  ${i.action.history.length?`<details class="hist-log"><summary>Aksiyon geçmişi <span class="hist-count">${i.action.history.length} kayıt</span></summary><ol class="hist-timeline">${i.action.history.slice().reverse().map(h=>`<li><div class="hl-when">${esc(h.at.replace("T"," ").replace("+00:00"," UTC"))}</div><div class="hl-what"><span class="hl-owner">${esc(h.owner)}</span>${h.previous_owner&&h.previous_owner!==h.owner?`<span class="hl-prev">önceki: ${esc(h.previous_owner)}</span>`:""}<div class="hl-move"><span class="hl-from">${statuses[h.from_status]}</span><span class="hl-arrow">→</span><span class="hl-to s-${esc(h.to_status)}">${statuses[h.to_status]}</span></div>${h.note?`<p class="hl-note">${esc(h.note)}</p>`:`<p class="hl-note empty">Not girilmedi.</p>`}</div></li>`).join("")}</ol><p class="subtle">Kayıtlar bellekte tutulur; kalıcı saklama için raporu indirin.</p></details>`:`<p class="subtle hist-empty">Henüz aksiyon kaydı yok. Sorumlu ve durum güncellendiğinde burada zaman damgalı geçmiş oluşur.</p>`}</div>
  <details class="trace-details"><summary>Ayrıntılı kanıt izi ve hesaplama</summary><div class="hypothesis"><p>${esc(i.explanation)}</p></div><div class="evidence">${i.evidence.map(e=>`<div class="evidence-item"><time>${time(e.timestamp)}</time><strong>${esc(e.alarm_type)}</strong><p>${esc(e.message)}</p><small>${esc(e.alarm_id)} · ${esc(e.host)}</small></div>`).join("")}</div>
  ${i.dependency_evidence?.length?`<details><summary>Bağlantı hedefleri ve doğrulanan yollar</summary><pre>${esc(JSON.stringify(i.dependency_evidence,null,2))}</pre></details>`:""}
  ${i.memory_trend?.length?`<details><summary>Bellek öncülleri · ${i.memory_trend.length} ölçümün tamamı</summary><div class="table-wrap"><table><thead><tr><th>HOST</th><th>ZAMAN</th><th>BELLEK</th><th>KANIT</th></tr></thead><tbody>${i.memory_trend.map(t=>`<tr><td>${esc(t.host)}</td><td>${time(t.timestamp)}</td><td>%${t.percent}</td><td>${esc(t.alarm_id)}</td></tr>`).join("")}</tbody></table></div></details>`:""}
  ${i.potential_services.length?`<details><summary>Grafikte olası ek etki: ${i.potential_services.length} servis</summary><p>Bu servislerde bu olaya bağlanan alarm yok. Topoloji gerçekleşmiş etkiyi tek başına kanıtlamaz.</p><div class="chips">${i.potential_services.map(service=>`<span class="chip">${esc(service)}</span>`).join("")}</div></details>`:""}
  <p>${esc(i.root.score_meaning)} ${i.root.score===null?"":"Skor: "+i.root.score}</p><pre>${esc(JSON.stringify(i.root.factors,null,2))}</pre><p>Öncelik: ${esc(i.priority.reason)}</p><p>${esc(i.confidence.meaning)}</p></details>
  <div class="detail-tools"><button class="secondary" id="inspect-alarms">${num(i.alarm_count)} ${review?"belirsiz kaydı":"alarmı"} incele ↗</button></div></div>`;
  $("jump-action").addEventListener("click",()=>{$("action-panel").scrollIntoView({behavior:"smooth",block:"center"});$("owner").focus({preventScroll:true});});
  $("assign-owner").addEventListener("click",()=>$("owner").focus());
  document.querySelectorAll("[data-action-status]").forEach(b=>b.addEventListener("click",()=>{$("status").value=b.dataset.actionStatus;$("action-note").focus();notify("Durum seçildi. Notu ekleyip Aksiyonu kaydet düğmesine basın.");}));
  $("action-form").addEventListener("submit",saveAction);
  $("inspect-alarms").addEventListener("click",()=>{switchTab("all",i.id);});
  $("narrative").addEventListener("click",async()=>{
    const button=$("narrative"), resultEl=$("narrative-result");button.disabled=true;button.textContent="Özet hazırlanıyor…";
    try {const result=await api(`/api/incidents/${encodeURIComponent(i.id)}/narrative`,{});resultEl.hidden=false;resultEl.className="narrative-result";resultEl.innerHTML=`<strong>${result.source==="llm"?"Model anlatısı":"Kanıta dayalı şablon"}</strong><p>${esc(result.summary)}</p><small>${esc(result.notice)}</small><small>Dayanak: ${result.evidence_ids.map(esc).join(", ")}</small>`;}
    catch(error){notify(error.message,true);}finally{button.disabled=false;button.textContent="Özeti göster";}
  });
}
async function saveAction(event) {
  event.preventDefault();const i=allCards().find(i=>i.id===selected), button=$("save-action");
  const body={owner:$("owner").value,status:$("status").value,note:$("action-note").value,version:i.action.version};button.disabled=true;
  try {i.action=await api(`/api/incidents/${encodeURIComponent(i.id)}/action`,body);if(selected===i.id)renderDetail();renderList();notify("Aksiyon ve geçmiş kaydedildi. Yeniden başlatmadan önce raporu dışa aktarabilirsiniz.");}
  catch(error){if(selected===i.id){$("action-error").textContent=error.message;$("action-error").hidden=false;}notify(error.message,true);}
  finally{button.disabled=false;}
}
let incidentFilter="";
function switchTab(name, filter="") {
  tab=name;offset=0;incidentFilter=filter;$("search").value="";
  document.querySelectorAll("[data-tab]").forEach(b=>{b.classList.toggle("active",b.dataset.tab===name);if(b.dataset.tab===name)b.setAttribute("aria-current","page");else b.removeAttribute("aria-current");});
  $("incidents-view").hidden=name!=="incidents";$("audit-view").hidden=!["noise","uncertain","all"].includes(name);$("metrics-view").hidden=name!=="metrics";
  if (["noise","uncertain","all"].includes(name))loadAlarms();
}
async function loadAlarms() {
  const serial=++requestSerial, names={noise:"Gürültü adayları",uncertain:"Belirsiz kayıtlar",all:"Tüm alarm kayıtları"};
  $("audit-title").textContent=incidentFilter?"Olaya bağlı alarm kayıtları":names[tab];
  $("audit-description").textContent=incidentFilter?`${incidentFilter} · Filtreden çıkmak için Tüm alarmlar sekmesine tıklayın.`:tab==="noise"?"Kesin gürültü etiketi değildir. Kayıtlar, elenme gerekçeleriyle birlikte korunur.":tab==="uncertain"?"Bağlantısı zayıf, adayları yarışan veya güçlü bir olaya atanamayan kayıtlar. İnceleme kartlarında gösterilen kayıtlar bu sınıfta kalır.":"Her alarm tek bir birincil karara sahiptir. Mesaj hedefi, karar gerekçesi ve aday puanları izlenebilir.";
  $("previous").disabled=true;$("next").disabled=true;
  const query=new URLSearchParams({offset,limit:PAGE,q:$("search").value});if(tab!=="all")query.set("decision",tab);if(incidentFilter)query.set("incident_id",incidentFilter);
  try {
    const result=await api("/api/alarms?"+query);if(serial!==requestSerial)return;total=result.total;
    $("audit-table").innerHTML=result.items.length?`<div class="table-wrap"><table><thead><tr><th>ZAMAN / ID</th><th>SERVİS / TİP</th><th>ŞİDDET</th><th>MESAJ VE KARAR GEREKÇESİ</th><th>KARAR</th></tr></thead><tbody>${result.items.map(a=>`<tr><td class="mono">${time(a.timestamp)}<small>${esc(a.alarm_id)}</small></td><td class="service">${esc(a.service)}<small class="mono">${esc(a.alarm_type)}</small><small>${esc(a.host)}</small></td><td><span class="badge ${a.severity>=4?"warn":"neutral"}">${a.severity}/5</span></td><td class="message">${esc(a.message)}<details><summary>Bu karar neden verildi?</summary><p>${esc(a.reason)}</p><small>Mesaj hedefi: ${esc(a.message_target||"tespit edilemedi")} · Bağımlılık yolu: ${a.target_relation&&a.target_relation!=="none"?esc(a.target_relation):"bulunamadı"} · Zamansal yoğunlaşma: ${a.concentration_ratio}× ${a.concentration_ratio<3?"(düşük — düzgün dağılmış)":a.concentration_ratio>=4?"(yüksek — olay sinyali)":"(orta)"}</small><pre>${esc(JSON.stringify(a.candidate_scores,null,2))}</pre></details></td><td><span class="badge ${a.decision==="incident"?"good":a.decision==="uncertain"?"warn":"neutral"}">${decisions[a.decision]}</span>${a.incident_id?`<small class="mono">${esc(a.incident_id)}</small>`:""}</td></tr>`).join("")}</tbody></table></div>`:'<div class="empty">Bu filtreye uygun alarm bulunamadı.</div>';
    $("page-info").textContent=total?`${num(offset+1)}–${num(Math.min(offset+PAGE,total))} / ${num(total)} kayıt`:"0 kayıt";
    $("previous").disabled=offset===0;$("next").disabled=offset+PAGE>=total;
  }catch(error){if(serial===requestSerial){$("audit-table").innerHTML=`<div class="notice error">${esc(error.message)}</div>`;$("page-info").textContent="İstek başarısız";}}
}
function renderMetrics() {
  const s=report.summary;
  $("metrics-view").innerHTML=`<div class="metrics-grid"><div class="panel"><div class="eyebrow">AYNI GİRDİ, İKİ GRUPLAMA</div><h2>Basit gruplamaya karşı</h2><div class="comparison"><div><strong>${s.naive_card_count}</strong><span>5 dakika × servis grubu</span></div><b>→</b><div class="accent"><strong>${s.incident_count}</strong><span>Kanıtlı olay adayı</span></div></div><p>Basit gruplama bütün alarmları gruplar. Bizim olay kartlarımız ${num(s.assigned_count)} alarmı kapsar; ${num(s.noise_count)} gürültü adayı ve ${num(s.uncertain_count)} belirsiz kayıt ayrı incelenir. Bu sayılar doğruluk kıyası değildir.</p><p>${num(s.input_count)} ham alarm → ${s.incident_count} olay kartı: görünümde %${((1-s.incident_count/s.input_count)*100).toFixed(2)} azalma. <strong>Gürültü tespit doğruluğu anlamına gelmez.</strong></p></div><div class="panel"><div class="eyebrow">KAPSAM VE İZLENEBİLİRLİK</div><h2>Her kayıt hesaba katılır</h2><p><strong>${num(s.assigned_count)} + ${num(s.noise_count)} + ${num(s.uncertain_count)} = ${num(s.input_count)}</strong></p><ul><li>${report.quality.unique_alarm_ids} benzersiz alarm kimliği.</li><li>${s.total_card_count} toplam kart (${s.incident_count} olay + ${s.review_candidate_count} inceleme) · 1–15 sınırı: ${s.card_limit_pass?"sağlandı":"sağlanmadı"}.</li><li>Tek çalıştırmada çekirdek süresi: ${s.elapsed_ms} ms (genel performans garantisi değil).</li><li>Olay sayısı ve servis adları koda sabitlenmez.</li><li>Aksiyonlar bellektedir; JSON raporu güncel durum geçmişini içerir.</li></ul></div></div>
  <div class="notice">${report.limitations.map(esc).join("<br>")}</div>
  <div class="section-heading"><div><h2>Alarm tipi bazında yoğunlaşma</h2><p>Eşit 10 dakika dilimlerinde tepe / max(medyan, 1). Oran yalnızca bağlamdır; tek başına olay veya gürültü kararı vermez. Tam gözlem penceresi kullanılır.</p></div></div>
  <div class="table-wrap"><table><thead><tr><th>ALARM TİPİ</th><th>KAYIT</th><th>MEDYAN / PAYDA</th><th>TEPE</th><th>YOĞUNLAŞMA</th><th>TEPE Z-SKORU</th><th>BAĞLAM</th></tr></thead><tbody>${report.baseline.types.slice().sort((a,b)=>b.ratio-a.ratio).map(t=>`<tr><td class="mono">${esc(t.alarm_type)}</td><td>${t.count}</td><td>${t.median} / ${t.denominator}</td><td>${t.peak}</td><td>${t.ratio}×</td><td>${t.peak_z}</td><td>${esc(t.role)}</td></tr>`).join("")}</tbody></table></div>
  <div class="metrics-grid"><div class="panel"><h3>Veri kalitesi notları</h3>${report.quality.warnings.map(w=>`<p>${esc(w)}</p>`).join("")}<p>Mesaj hedefi / grafik ilişkisi:</p><pre>${esc(JSON.stringify(report.quality.target_relations,null,2))}</pre></div><div class="panel"><h3>Kaynak parmak izleri · SHA-256</h3>${Object.entries(report.quality.manifest).map(([name,hash])=>`<p><strong>${esc(name)}</strong><br><span class="hash">${esc(hash)}</span></p>`).join("")}</div></div>`;
}
document.querySelectorAll("[data-tab]").forEach(b=>b.addEventListener("click",()=>{if(report)switchTab(b.dataset.tab);}));
$("refresh").addEventListener("click",load);
$("search").addEventListener("input",()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{offset=0;loadAlarms();},200);});
$("previous").addEventListener("click",()=>{offset=Math.max(0,offset-PAGE);loadAlarms();});
$("next").addEventListener("click",()=>{offset+=PAGE;loadAlarms();});
load();
