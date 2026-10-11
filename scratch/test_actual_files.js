const { spawn } = require('child_process');
const fs = require('fs');

async function testActualFiles() {
  const chromeProcess = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
    '--headless=new',
    '--remote-debugging-port=9227',
    '--user-data-dir=/tmp/chrome_test_actual_' + Date.now(),
    '--no-first-run',
    '--no-default-browser-check'
  ]);

  await new Promise(r => setTimeout(r, 1200));

  try {
    const listRes = await fetch('http://127.0.0.1:9227/json/list');
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

    console.log('Navigating to local index.html (testing real file changes)...');
    await send('Page.navigate', {
      url: 'file:///Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/OncologiaRobotica/index.html'
    });
    await new Promise(r => setTimeout(r, 2000));

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
      // also synthetic click
      await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
      await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
    };

    console.log('1. Checking initial closed state...');
    const initCheck = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const btn = document.querySelector('.menu-button-4');
          const menu = document.querySelector('.nav-menu-3');
          return {
            btnClasses: btn.className,
            menuDisplay: window.getComputedStyle(menu).display
          };
        })()
      `,
      returnByValue: true
    });
    console.log('Init state:', initCheck.result.value);

    console.log('2. Tapping menu button to open...');
    await tapSelector('.menu-button-4');
    await new Promise(r => setTimeout(r, 400));

    const openCheck = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const btn = document.querySelector('.menu-button-4');
          const menu = document.querySelector('.nav-menu-3');
          const r = menu.getBoundingClientRect();
          return {
            btnClasses: btn.className,
            menuDisplay: window.getComputedStyle(menu).display,
            rect: { top: r.top, left: r.left, width: r.width, height: r.height }
          };
        })()
      `,
      returnByValue: true
    });
    console.log('Open state:', openCheck.result.value);

    const ssOpen = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync('/Users/fanssimarketingdigital/.gemini/antigravity/brain/ae798c42-e236-4a06-8dde-1e2e064fe54e/scratch/verify_actual_open.png', Buffer.from(ssOpen.data, 'base64'));

    console.log('3. Tapping menu button to close...');
    await tapSelector('.menu-button-4');
    await new Promise(r => setTimeout(r, 400));

    const closedCheck = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const btn = document.querySelector('.menu-button-4');
          const menu = document.querySelector('.nav-menu-3');
          return {
            btnClasses: btn.className,
            menuDisplay: window.getComputedStyle(menu).display
          };
        })()
      `,
      returnByValue: true
    });
    console.log('Closed state:', closedCheck.result.value);

    const ssClosed = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync('/Users/fanssimarketingdigital/.gemini/antigravity/brain/ae798c42-e236-4a06-8dde-1e2e064fe54e/scratch/verify_actual_closed.png', Buffer.from(ssClosed.data, 'base64'));

    console.log('Verification completed successfully!');

  } catch (err) {
    console.error('Error during actual files test:', err);
  } finally {
    chromeProcess.kill();
    process.exit(0);
  }
}

testActualFiles();
