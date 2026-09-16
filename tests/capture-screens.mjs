// Ekran goruntusu uretici: calisan uygulamadan demo/ altina PNG kaydeder.
// Gereksinim: Chrome --headless=new --remote-debugging-port=9222 ve ayakta bir uygulama.
// Kullanim: node tests/capture-screens.mjs
import fs from 'node:fs/promises';

const APP = process.env.APP_URL || 'http://127.0.0.1:8000';
const DEBUG = process.env.CHROME_DEBUG_URL || 'http://127.0.0.1:9222';
const OUT = process.env.OUT_DIR || 'demo';

const target = await (await fetch(DEBUG + '/json/new?about:blank')).json().catch(async () => {
  const list = await (await fetch(DEBUG + '/json/list')).json();
  return list.find(p => p.type === 'page');
});
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.addEventListener('open', res, { once: true }); ws.addEventListener('error', rej, { once: true }); });

let seq = 0;
const pending = new Map();
ws.addEventListener('message', e => {
  const msg = JSON.parse(e.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg.result); pending.delete(msg.id); }
});
const send = (method, params = {}) => new Promise(res => { const id = ++seq; pending.set(id, res); ws.send(JSON.stringify({ id, method, params })); });
const wait = ms => new Promise(r => setTimeout(r, ms));

await send('Page.enable');
await send('Runtime.enable');

async function shot(name, { width = 1600, height = 1200, script = null, settle = 1400, full = false } = {}) {
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 2, mobile: width < 700 });
  if (script) { await send('Runtime.evaluate', { expression: script, awaitPromise: true }); await wait(settle); }
  const { data } = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: full });
  await fs.writeFile(`${OUT}/${name}.png`, Buffer.from(data, 'base64'));
  console.log(`  ${name}.png yazildi (${width}x${height})`);
}

console.log('Ekran goruntuleri aliniyor...');
await send('Page.navigate', { url: APP });
await wait(3500);

// 1) Operasyon masasi — ust bolum
await shot('operasyon-masasi', { script: 'window.scrollTo(0,0)' });

// 2) Olay zaman cizelgesi
await shot('zaman-cizelgesi', {
  script: `document.getElementById('gantt-wrap').scrollIntoView({block:'center'})`
});

// 3) Olay karti — kanit + AI seridi
await shot('olay-karti', {
  script: `document.querySelector('.ai-strip').scrollIntoView({block:'start'});window.scrollBy(0,-90)`
});

// 4) Benzer gecmis olaylar (B3) acik
await shot('benzer-gecmis-olaylar', {
  script: `const d=[...document.querySelectorAll('details.sec')].find(x=>x.textContent.includes('BENZER GEÇMİŞ'));if(d){d.open=true;d.scrollIntoView({block:'center'});}`
});

// 5) Yontem ve olcum sekmesi
await shot('yontem-ve-olcum', {
  script: `document.querySelector('[data-tab="metrics"]').click();window.scrollTo(0,320)`,
  settle: 1600
});

// 6) Alarm izlenebilirligi (tum alarmlar)
await shot('alarm-izlenebilirligi', {
  script: `document.querySelector('[data-tab="all"]').click();window.scrollTo(0,320)`,
  settle: 2200
});

// 7) Mobil gorunum
await send('Page.navigate', { url: APP });
await wait(3000);
await shot('mobil', { width: 430, height: 940, script: 'window.scrollTo(0,0)' });

console.log('Tamamlandi.');
ws.close();
process.exit(0);
