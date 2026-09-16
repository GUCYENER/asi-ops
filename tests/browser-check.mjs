// Optional UI verification: Node 22+ and a separate Chrome --remote-debugging-port=9222.
// Run against a disposable app instance; this test changes one action.
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';

const app = process.env.TEST_APP_URL || 'http://127.0.0.1:8001';
const debug = process.env.CHROME_DEBUG_URL || 'http://127.0.0.1:9222';
const pages = await (await fetch(debug + '/json/list')).json();
const page = pages.find(p => p.type === 'page');
assert.ok(page, 'Chrome page available');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{ws.addEventListener('open',resolve,{once:true});ws.addEventListener('error',reject,{once:true});});
let sequence=0;
const pending=new Map(), errors=[];
ws.addEventListener('message', event=>{
  const message=JSON.parse(event.data);
  if(message.id){const p=pending.get(message.id);if(p){pending.delete(message.id);message.error?p.reject(new Error(message.error.message)):p.resolve(message.result);}}
  if(message.method==='Runtime.exceptionThrown')errors.push(message.params.exceptionDetails.text);
  if(message.method==='Log.entryAdded' && message.params.entry.level==='error' && !message.params.entry.url?.endsWith('/favicon.ico'))errors.push(message.params.entry.text);
});
function cdp(method,params={}) {return new Promise((resolve,reject)=>{const id=++sequence;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});}
async function evaluate(expression){const r=await cdp('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function waitFor(expression){for(let i=0;i<100;i++){if(await evaluate(expression))return;await new Promise(r=>setTimeout(r,60));}throw new Error('Timed out: '+expression);}
async function screenshot(name){const {data}=await cdp('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});await fs.writeFile(new URL('../demo/'+name,import.meta.url),Buffer.from(data,'base64'));}

try {
  await fs.mkdir(new URL('../demo/',import.meta.url),{recursive:true});
  await cdp('Runtime.enable');await cdp('Log.enable');await cdp('Page.enable');
  await cdp('Emulation.setDeviceMetricsOverride',{width:1440,height:1100,deviceScaleFactor:1,mobile:false});
  await cdp('Page.navigate',{url:app});
  await waitFor('document.querySelectorAll(".incident-card").length > 0');
  assert.equal(await evaluate('document.querySelectorAll(".incident-card[data-card-type=incident]").length'),5);
  assert.equal(await evaluate('document.querySelectorAll(".incident-card[data-card-type=review]").length'),3);
  assert.equal(await evaluate('document.getElementById("error").hidden'),true);
  assert.match(await evaluate('document.querySelector(".executive-meta").textContent'),/9 host/);
  assert.equal(await evaluate('document.querySelector(".trace-details").open'),false);
  assert.ok(await evaluate('document.querySelectorAll(".evidence-checks li").length >= 3'));
  assert.equal(await evaluate('document.documentElement.scrollWidth <= window.innerWidth'),true);
  await screenshot('operasyon-masasi.png');
  await evaluate('document.querySelector("[data-tab=noise]").click()');
  await waitFor('document.querySelectorAll("#audit-table tbody tr").length === 50');
  assert.match(await evaluate('document.getElementById("page-info").textContent'),/1–50/);
  await evaluate('document.getElementById("next").click()');
  await waitFor('document.getElementById("page-info").textContent.startsWith("51–100")');
  await evaluate('document.querySelector("[data-tab=all]").click(); document.getElementById("search").value="mobile-bff"; document.getElementById("search").dispatchEvent(new Event("input"));');
  await waitFor('document.querySelectorAll("#audit-table td.service").length > 0 && Array.from(document.querySelectorAll("#audit-table td.service")).every(e=>e.textContent.startsWith("mobile-bff"))');
  await evaluate('document.querySelector("#audit-table details").open=true');
  await screenshot('alarm-izlenebilirligi.png');
  await evaluate('document.querySelector("[data-tab=metrics]").click()');
  assert.match(await evaluate('document.getElementById("metrics-view").textContent'),/578/);
  await screenshot('yontem-ve-olcum.png');
  await evaluate('document.querySelector("[data-tab=incidents]").click();document.querySelector("[data-card-type=review]").click()');
  assert.match(await evaluate('document.getElementById("incident-detail").textContent'),/Düşük kanıtlı inceleme/);
  await evaluate('document.getElementById("inspect-alarms").click()');
  await waitFor('document.querySelectorAll("#audit-table tbody tr").length===44');
  assert.equal(await evaluate('Array.from(document.querySelectorAll("#audit-table tbody tr td:last-child")).every(e=>e.textContent.includes("Belirsiz"))'),true);
  await evaluate('document.querySelector("[data-tab=incidents]").click();document.querySelector("[data-card-type=incident]").click()');
  await evaluate('document.querySelector("[data-tab=incidents]").click();document.getElementById("status").value="investigating"; document.getElementById("owner").value="UI test nöbetçisi";document.getElementById("action-note").value="Tarayıcı testi: incelemeye alındı";document.getElementById("action-form").requestSubmit();');
  await waitFor('document.querySelector(".history")?.textContent.includes("Tarayıcı testi")');
  await evaluate('document.getElementById("status").value="resolved"; document.getElementById("action-note").value="Tarayıcı testi tamamlandı; fiziksel müdahale yapılmadı"; document.getElementById("action-form").requestSubmit();');
  await waitFor('document.querySelector(".history")?.textContent.includes("fiziksel müdahale")');
  await evaluate('document.getElementById("narrative").click()');
  await waitFor('!document.getElementById("narrative-result").hidden');
  assert.match(await evaluate('document.getElementById("narrative-result").textContent'),/şablon/);
  await cdp('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
  await evaluate('window.scrollTo(0,0);document.getElementById("toast").hidden=true');
  assert.equal(await evaluate('document.documentElement.scrollWidth <= window.innerWidth'),true,'No horizontal mobile overflow');
  await screenshot('mobil.png');
  assert.deepEqual(errors,[],'No JavaScript / CSP errors');
  console.log(JSON.stringify({passed:true,checks:['desktop_render','mobile_no_overflow','audit_pagination','search','decision_details','metrics','review_card_and_filter','action_investigate_resolve','template_fallback'],screenshots:4,errors},null,2));
} finally {ws.close();}
