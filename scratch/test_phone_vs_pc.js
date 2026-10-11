const { spawn } = require('child_process');
const fs = require('fs');

async function testMobileTouch() {
  const chromeProcess = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
    '--headless=new',
    '--remote-debugging-port=9223',
    '--user-data-dir=/tmp/chrome_test_touch_' + Date.now(),
    '--no-first-run',
    '--no-default-browser-check'
  ]);

  await new Promise(r => setTimeout(r, 1500));

  try {
    const listRes = await fetch('http://127.0.0.1:9223/json/list');
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

    // Emulate iPhone 14 / mobile touch screen
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

    console.log('Navigating to live production: https://oncologia-robotica.com/ ...');
    await send('Page.navigate', { url: 'https://oncologia-robotica.com/' });
    await new Promise(r => setTimeout(r, 3500));

    // Check DOM state
    const info1 = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const btn = document.querySelector('.menu-button-4');
          const menu = document.querySelector('.nav-menu-3');
          const nav = document.querySelector('.navbar-4');
          const rect = btn ? btn.getBoundingClientRect() : null;
          return {
            hasTouchClass: document.documentElement.className,
            btnRect: rect ? { top: rect.top, left: rect.left, width: rect.width, height: rect.height } : null,
            btnDisplay: btn ? window.getComputedStyle(btn).display : null,
            menuDisplay: menu ? window.getComputedStyle(menu).display : null,
            menuTop: menu ? window.getComputedStyle(menu).top : null,
            navClasses: nav ? nav.className : null
          };
        })()
      `,
      returnByValue: true
    });
    console.log('Initial state on production:', info1.result.value);

    // Let's get coordinates of center of menu button
    const btnCoords = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const btn = document.querySelector('.menu-button-4');
          const r = btn.getBoundingClientRect();
          return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()
      `,
      returnByValue: true
    });
    const { x, y } = btnCoords.result.value;
    console.log('Button coordinates:', x, y);

    // Track all events on button and document
    await send('Runtime.evaluate', {
      expression: `
        window.__eventsLog = [];
        const btn = document.querySelector('.menu-button-4');
        ['touchstart', 'touchend', 'click', 'pointerdown', 'pointerup'].forEach(type => {
          btn.addEventListener(type, (e) => {
            window.__eventsLog.push({ target: 'btn', type, time: Date.now() });
          }, true);
          document.addEventListener(type, (e) => {
            window.__eventsLog.push({ target: 'doc', type, time: Date.now(), isBtn: btn.contains(e.target) });
          }, true);
        });
      `
    });

    // SIMULATE REAL MOBILE PHONE TAP: touchstart, touchend, then delayed synthetic click
    console.log('Simulating mobile phone tap...');
    await send('Input.dispatchTouchEvent', {
      type: 'touchStart',
      touchPoints: [{ x, y }]
    });
    await new Promise(r => setTimeout(r, 60));
    await send('Input.dispatchTouchEvent', {
      type: 'touchEnd',
      touchPoints: []
    });

    // Wait 50ms and check state
    await new Promise(r => setTimeout(r, 50));
    const afterTouch = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const btn = document.querySelector('.menu-button-4');
          const menu = document.querySelector('.nav-menu-3');
          const overlay = document.querySelector('.w-nav-overlay');
          const mRect = menu ? menu.getBoundingClientRect() : null;
          return {
            step: 'afterTouch',
            btnClasses: btn ? btn.className : null,
            menuDisplay: menu ? window.getComputedStyle(menu).display : null,
            menuParent: menu ? menu.parentElement.className : null,
            menuRect: mRect ? { top: mRect.top, left: mRect.left, height: mRect.height } : null,
            overlayExists: !!overlay,
            overlayDisplay: overlay ? window.getComputedStyle(overlay).display : null,
            overlayHeight: overlay ? overlay.style.height : null
          };
        })()
      `,
      returnByValue: true
    });
    console.log('State immediately after touchEnd:', afterTouch.result.value);

    // Dispatch synthetic mouse click (like mobile Safari / Chrome does)
    await send('Input.dispatchMouseEvent', {
      type: 'mousePressed',
      x,
      y,
      button: 'left',
      clickCount: 1
    });
    await send('Input.dispatchMouseEvent', {
      type: 'mouseReleased',
      x,
      y,
      button: 'left',
      clickCount: 1
    });

    await new Promise(r => setTimeout(r, 300));
    const afterClick = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const btn = document.querySelector('.menu-button-4');
          const menu = document.querySelector('.nav-menu-3');
          const overlay = document.querySelector('.w-nav-overlay');
          const mRect = menu ? menu.getBoundingClientRect() : null;
          return {
            step: 'afterSyntheticClick',
            btnClasses: btn ? btn.className : null,
            menuDisplay: menu ? window.getComputedStyle(menu).display : null,
            menuParent: menu ? menu.parentElement.className : null,
            menuRect: mRect ? { top: mRect.top, left: mRect.left, height: mRect.height } : null,
            overlayExists: !!overlay,
            overlayDisplay: overlay ? window.getComputedStyle(overlay).display : null,
            overlayHeight: overlay ? overlay.style.height : null,
            events: window.__eventsLog
          };
        })()
      `,
      returnByValue: true
    });
    console.log('State after synthetic click:\n', JSON.stringify(afterClick.result.value, null, 2));

    const ss = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync('/Users/fanssimarketingdigital/.gemini/antigravity/brain/ae798c42-e236-4a06-8dde-1e2e064fe54e/scratch/mobile_live_touch.png', Buffer.from(ss.data, 'base64'));
    console.log('Saved screenshot to scratch/mobile_live_touch.png');

  } catch (err) {
    console.error('Test error:', err);
  } finally {
    chromeProcess.kill();
    process.exit(0);
  }
}

testMobileTouch();
