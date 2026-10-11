const { spawn } = require('child_process');
const fs = require('fs');

async function testLiveProduction() {
  const chromeProcess = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
    '--headless=new',
    '--remote-debugging-port=9228',
    '--user-data-dir=/tmp/chrome_live_prod_' + Date.now(),
    '--no-first-run',
    '--no-default-browser-check'
  ]);

  await new Promise(r => setTimeout(r, 1200));

  try {
    const listRes = await fetch('http://127.0.0.1:9228/json/list');
    const targets = await listRes.json();
    const target = targets.find(t => t.type === 'page') || targets[0];
    const ws = new WebSocket(target.webSocketDebuggerUrl);

    let id = 1;
    function send(method, params = {}) {
      return new Promise((resolve, reject) => {
        const msgId = id++;
        const handler = (evt) => {
          const res = JSON.parse(evt.data);
          if (res.id === msgId) {
            ws.removeEventListener('message', handler);
            if (res.error) reject(res.error);
            else resolve(res.result);
          }
        };
        ws.addEventListener('message', handler);
        ws.send(JSON.stringify({ id: msgId, method, params }));
      });
    }

    await new Promise(r => ws.addEventListener('open', r));
    await send('Page.enable');
    await send('Runtime.enable');

    // Emulate iPhone
    await send('Emulation.setDeviceMetricsOverride', {
      width: 390,
      height: 844,
      deviceScaleFactor: 3,
      mobile: true,
      hasTouch: true
    });
    await send('Emulation.setTouchEmulationEnabled', {
      enabled: true,
      maxTouchPoints: 5
    });

    console.log('Navigating to LIVE: https://oncologia-robotica.com/ ...');
    await send('Page.navigate', { url: 'https://oncologia-robotica.com/?v=' + Date.now() });
    await new Promise(r => setTimeout(r, 3000));

    const tapSelector = async (sel) => {
      const coords = await send('Runtime.evaluate', {
        expression: `
          (() => {
            const el = document.querySelector('${sel}');
            if (!el) return null;
            const r = el.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
          })()
        `,
        returnByValue: true
      });
      if (!coords.result.value) throw new Error('Element not found: ' + sel);
      const { x, y } = coords.result.value;

      await send('Input.dispatchTouchEvent', {
        type: 'touchStart',
        touchPoints: [{ x, y }]
      });
      await new Promise(r => setTimeout(r, 60));
      await send('Input.dispatchTouchEvent', {
        type: 'touchEnd',
        touchPoints: []
      });
      await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
      await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
    };

    console.log('1. Check initial state on LIVE...');
    const initCheck = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const btn = document.querySelector('.menu-button-4');
          const menu = document.querySelector('.nav-menu-3');
          return {
            btnClasses: btn ? btn.className : null,
            menuDisplay: menu ? window.getComputedStyle(menu).display : null
          };
        })()
      `,
      returnByValue: true
    });
    console.log('Live Init state:', initCheck.result.value);

    console.log('2. Tapping live menu button to open...');
    await tapSelector('.menu-button-4');
    await new Promise(r => setTimeout(r, 500));

    const openCheck = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const btn = document.querySelector('.menu-button-4');
          const menu = document.querySelector('.nav-menu-3');
          const r = menu ? menu.getBoundingClientRect() : null;
          return {
            btnClasses: btn ? btn.className : null,
            menuDisplay: menu ? window.getComputedStyle(menu).display : null,
            rect: r ? { top: r.top, left: r.left, width: r.width, height: r.height } : null
          };
        })()
      `,
      returnByValue: true
    });
    console.log('Live Open state:', openCheck.result.value);

    const ssOpen = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync('/Users/fanssimarketingdigital/.gemini/antigravity/brain/ae798c42-e236-4a06-8dde-1e2e064fe54e/scratch/live_prod_open.png', Buffer.from(ssOpen.data, 'base64'));

    console.log('3. Tapping live menu button to close...');
    await tapSelector('.menu-button-4');
    await new Promise(r => setTimeout(r, 500));

    const closedCheck = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const btn = document.querySelector('.menu-button-4');
          const menu = document.querySelector('.nav-menu-3');
          return {
            btnClasses: btn ? btn.className : null,
            menuDisplay: menu ? window.getComputedStyle(menu).display : null
          };
        })()
      `,
      returnByValue: true
    });
    console.log('Live Closed state:', closedCheck.result.value);

    const ssClosed = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync('/Users/fanssimarketingdigital/.gemini/antigravity/brain/ae798c42-e236-4a06-8dde-1e2e064fe54e/scratch/live_prod_closed.png', Buffer.from(ssClosed.data, 'base64'));

    console.log('Live production smoke test completed!');

  } catch (err) {
    console.error('Live test error:', err);
  } finally {
    chromeProcess.kill();
    process.exit(0);
  }
}

testLiveProduction();
