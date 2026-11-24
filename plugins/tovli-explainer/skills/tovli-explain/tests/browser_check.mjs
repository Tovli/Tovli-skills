// Optional browser regression check. Requires Node 22+ and a Chromium browser.
// Usage: node browser_check.mjs <browser-executable> <report.html>
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {pathToFileURL} from 'node:url';

const [browserPath, reportPath] = process.argv.slice(2);
if (!browserPath || !reportPath) throw new Error('Pass a Chromium executable and example report path.');
const workspace = await fs.mkdtemp(path.join(os.tmpdir(), 'tovli-explain-browser-'));
const port = await new Promise(resolve => {
  const server = net.createServer();
  server.listen(0, '127.0.0.1', () => {
    const selected = server.address().port;
    server.close(() => resolve(selected));
  });
});
const browser = spawn(browserPath, [
  '--headless=new', '--no-first-run', '--no-default-browser-check',
  '--remote-debugging-address=127.0.0.1', '--remote-debugging-port=' + port,
  '--user-data-dir=' + path.join(workspace, 'profile'), 'about:blank',
], {windowsHide: true, stdio: 'ignore'});
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
let socket, serial = 0, session, requests = [];
const pending = new Map();
function send(method, params = {}, sessionId = session) {
  return new Promise((resolve, reject) => {
    const id = ++serial;
    pending.set(id, {resolve, reject});
    socket.send(JSON.stringify({id, method, params, ...(sessionId ? {sessionId} : {})}));
  });
}
async function evaluate(expression) {
  const result = await send('Runtime.evaluate', {expression, awaitPromise: true, returnByValue: true});
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
}
async function screenshot(name) {
  const result = await send('Page.captureScreenshot', {format: 'png'});
  await fs.writeFile(path.join(workspace, name + '.png'), Buffer.from(result.data, 'base64'));
}
async function settleMotion() {
  await evaluate('new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))');
}
async function scrollTo(top) {
  await evaluate(`window.scrollTo({top: ${top}, behavior: 'instant'})`);
  await settleMotion();
}
async function motionState() {
  return evaluate(`(() => {
    const layers = [...document.querySelectorAll('.hero-art [data-parallax]')];
    const progress = document.querySelector('.reading-progress');
    const progressStyle = progress && getComputedStyle(progress);
    return {
      transforms: layers.map(layer => getComputedStyle(layer).transform),
      static: layers.every(layer => new DOMMatrixReadOnly(getComputedStyle(layer).transform).isIdentity),
      progress: Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--read-progress')),
      progressStyle: progressStyle && [progressStyle.transform, progressStyle.width],
      scrollY,
    };
  })()`);
}
async function assertContentVisible() {
  assert.equal(await evaluate(`(() => {
    const content = [...document.querySelectorAll('.hero h1, [data-view]:not([hidden]) .step')]
      .filter(element => element.closest('[data-view]') ? getComputedStyle(element.closest('[data-view]')).display !== 'none' : true);
    return content.length > 1 && content.every(element => {
      const style = getComputedStyle(element);
      return element.getClientRects().length > 0 && style.visibility === 'visible' && Number(style.opacity) > 0;
    });
  })()`), true, 'Motion settings hid report content.');
}
async function assertStaticMotion(label) {
  await scrollTo(0);
  const start = await motionState();
  await scrollTo(260);
  const end = await motionState();
  assert.equal(start.static && end.static, true, label + ' should leave decorative layers at their natural position.');
  assert.deepEqual(end.transforms, start.transforms, label + ' should disable parallax while scrolling.');
  await assertContentVisible();
}
try {
  let endpoint;
  for (let attempt = 0; attempt < 100; attempt++) {
    try {
      const response = await fetch('http://127.0.0.1:' + port + '/json/version');
      endpoint = (await response.json()).webSocketDebuggerUrl;
      break;
    } catch { await delay(100); }
  }
  assert.ok(endpoint, 'Browser did not start.');
  socket = new WebSocket(endpoint);
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, {once: true});
    socket.addEventListener('error', reject, {once: true});
  });
  socket.addEventListener('message', event => {
    const result = JSON.parse(event.data);
    if (result.id && pending.has(result.id)) {
      const callback = pending.get(result.id);
      pending.delete(result.id);
      result.error ? callback.reject(new Error(JSON.stringify(result.error))) : callback.resolve(result.result);
    }
    if (result.method === 'Network.requestWillBeSent') requests.push(result.params.request.url);
    if (result.method === 'Runtime.exceptionThrown') requests.push('SCRIPT ERROR: ' + JSON.stringify(result.params));
  });
  const target = await send('Target.createTarget', {url: 'about:blank'}, null);
  session = (await send('Target.attachToTarget', {targetId: target.targetId, flatten: true}, null)).sessionId;
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Network.enable');
  await send('Emulation.setDeviceMetricsOverride', {width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false});
  await send('Emulation.setEmulatedMedia', {features: [{name: 'prefers-reduced-motion', value: 'no-preference'}]});
  await send('Page.navigate', {url: pathToFileURL(path.resolve(reportPath)).href});
  for (let attempt = 0; attempt < 50; attempt++) {
    if (await evaluate("document.readyState === 'complete' && !!document.querySelector('#view-business .step')")) break;
    await delay(100);
  }
  const visibility = () => evaluate("Array.from(document.querySelectorAll('[data-view]')).filter(x => getComputedStyle(x).display !== 'none').map(x => x.dataset.view)");
  assert.deepEqual(await visibility(), ['business']);
  assert.equal(await evaluate("document.body.innerText.includes('src/Invoices')"), false);
  assert.equal(await evaluate("document.body.innerText.includes('HTTP 404')"), false);
  assert.equal(await evaluate(`(() => {
    const layers = [...document.querySelectorAll('[data-parallax]')];
    return layers.length > 0 && layers.every(layer => layer.closest('.hero-art[aria-hidden="true"]')
      && !layer.closest('.step, .visual-card, svg, h1, h2, p'));
  })()`), true, 'Parallax must apply only to decorative, accessibility-hidden hero layers.');
  await scrollTo(0);
  const heroStart = await motionState();
  assert.equal(Number.isFinite(heroStart.progress), true, 'Reading progress must expose a numeric value.');
  await screenshot('hero-desktop');
  await scrollTo(260);
  const heroScrolled = await motionState();
  assert.equal(heroScrolled.scrollY, 260, 'Desktop scrolling should remain native.');
  assert.equal(heroScrolled.transforms.some((transform, index) => transform !== heroStart.transforms[index]), true,
    'Desktop scroll should move decorative hero layers.');
  assert.ok(heroScrolled.progress > heroStart.progress, 'Reading progress should advance with scrolling.');
  assert.notDeepEqual(heroScrolled.progressStyle, heroStart.progressStyle, 'Reading progress must visibly advance.');
  assert.equal(await evaluate(`Array.from(document.querySelectorAll('.hero h1, .hero p, .step, .visual-card'))
    .every(element => getComputedStyle(element).transform === 'none')`), true,
  'Scene text and diagram cards must remain stationary.');
  await send('Emulation.setEmulatedMedia', {features: [{name: 'prefers-reduced-motion', value: 'reduce'}]});
  await settleMotion();
  assert.equal((await motionState()).static, true, 'Enabling reduced motion must reset existing transforms immediately.');
  await assertStaticMotion('Reduced motion');
  await send('Emulation.setEmulatedMedia', {features: [{name: 'prefers-reduced-motion', value: 'no-preference'}]});
  await settleMotion();
  assert.equal((await motionState()).static, false, 'Disabling reduced motion should restore desktop parallax at the current scroll position.');
  await evaluate("document.getElementById('scene-1').scrollIntoView({block:'center'})");
  await delay(150);
  assert.equal(await evaluate("document.querySelector('#view-business .visual-card').dataset.scene"), '1');
  assert.equal(await evaluate("document.querySelector('#view-business .visual-card svg') !== null"), true);
  await screenshot('business-desktop');
  await evaluate("document.getElementById('tab-technical').click()");
  await delay(150);
  assert.deepEqual(await visibility(), ['technical']);
  assert.equal(await evaluate("document.body.innerText.includes('HTTP 404')"), true);
  await evaluate("document.getElementById('scene-3').scrollIntoView({block:'center'})");
  await delay(150);
  assert.equal(await evaluate("document.querySelector('#view-technical .visual-card').dataset.scene"), '3');
  await screenshot('technical-desktop');
  await evaluate("document.getElementById('tab-technical').focus()");
  await send('Input.dispatchKeyEvent', {type: 'keyDown', key: 'ArrowLeft', code: 'ArrowLeft'});
  await send('Input.dispatchKeyEvent', {type: 'keyUp', key: 'ArrowLeft', code: 'ArrowLeft'});
  assert.deepEqual(await visibility(), ['business']);
  await send('Emulation.setDeviceMetricsOverride', {width: 390, height: 844, deviceScaleFactor: 1, mobile: true});
  await settleMotion();
  await assertStaticMotion('Mobile viewport');
  await evaluate("document.getElementById('scene-1').scrollIntoView({block:'start'})");
  await delay(150);
  assert.deepEqual(await visibility(), ['business']);
  assert.equal(await evaluate("getComputedStyle(document.querySelector('#view-business .visual-wrap')).display"), 'none');
  assert.equal(await evaluate("innerWidth"), 390, 'Mobile layout expanded beyond its viewport.');
  assert.equal(await evaluate("getComputedStyle(document.querySelector('#view-business .mobile-visual')).display"), 'block');
  assert.equal(await evaluate("document.documentElement.scrollWidth <= innerWidth"), true);
  assert.equal(await evaluate("document.body.innerText.includes('HTTP 404')"), false);
  await screenshot('business-mobile');
  await evaluate("document.getElementById('tab-technical').click()");
  await delay(150);
  assert.deepEqual(await visibility(), ['technical']);
  assert.equal(await evaluate("document.documentElement.scrollWidth <= innerWidth"), true);
  await screenshot('technical-mobile');
  await send('Emulation.setDeviceMetricsOverride', {width: 320, height: 740, deviceScaleFactor: 1, mobile: true});
  await settleMotion();
  await assertStaticMotion('Narrow viewport');
  for (const view of ['business', 'technical']) {
    await evaluate(`document.getElementById('tab-${view}').click()`);
    await settleMotion();
    assert.deepEqual(await visibility(), [view]);
    assert.equal(await evaluate('innerWidth'), 320, 'Narrow layout expanded beyond its viewport.');
    assert.equal(await evaluate('document.documentElement.scrollWidth <= innerWidth'), true, view + ' view overflowed at 320px.');
  }
  await send('Emulation.setDeviceMetricsOverride', {width: 816, height: 1056, deviceScaleFactor: 1, mobile: false});
  await send('Emulation.setEmulatedMedia', {media: 'print'});
  await settleMotion();
  assert.deepEqual(await visibility(), ['technical'], 'Printing must preserve the selected view.');
  assert.equal(await evaluate("getComputedStyle(document.querySelector('.hero-art')).display"), 'none',
    'Print output must hide decorative hero art.');
  assert.equal(await evaluate("getComputedStyle(document.querySelector('#view-technical .visual-wrap')).display"), 'none');
  assert.equal(await evaluate("getComputedStyle(document.querySelector('#view-technical .mobile-visual')).display"), 'block',
    'Print output must include inline diagrams.');
  assert.equal(await evaluate('document.documentElement.scrollWidth <= innerWidth'), true, 'Print layout overflowed its page width.');
  await assertContentVisible();
  assert.equal(requests.some(url => /^https?:/.test(url)), false, 'Report requested an external resource.');
  assert.equal(requests.some(url => url.startsWith('SCRIPT ERROR:')), false, 'Report had a JavaScript error.');
  console.log('Browser checks passed: decorative parallax, reading progress, live reduced motion, exclusive views, activity/component visuals, keyboard navigation, 390px/320px layouts, print layout, and offline loading.');
  console.log('Screenshots: ' + workspace);
} finally {
  if (socket?.readyState === WebSocket.OPEN) {
    // Browser.close shuts down the browser and its child processes.
    await send('Browser.close', {}, null).catch(() => {});
    socket.close();
  } else {
    browser.kill();
  }
}
