const { spawn } = require('child_process');
const fs = require('fs');

async function testTouchOnLocal() {
  const chromeProcess = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
    '--headless=new',
    '--remote-debugging-port=9224',
    '--user-data-dir=/tmp/chrome_test_touch_local_' + Date.now(),
    '--no-first-run',
    '--no-default-browser-check'
  ]);

  await new Promise(r => setTimeout(r, 1500));

  try {
    const listRes = await fetch('http://127.0.0.1:9224/json/list');
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

    // Emulate iPhone / Mobile
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

    console.log('Navigating to local index.html...');
    await send('Page.navigate', {
      url: 'file:///Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/OncologiaRobotica/index.html'
    });
    await new Promise(r => setTimeout(r, 2000));

    // Apply the proposed CSS & configuration fixes directly to DOM
    await send('Runtime.evaluate', {
      expression: `
        (() => {
          const nav = document.querySelector('.navbar-4');
          nav.setAttribute('data-animation', 'none');
          nav.setAttribute('data-duration', '0');

          // Inject the fixed CSS
          const style = document.createElement('style');
          style.id = 'fix-style';
          style.textContent = \`
            @media screen and (max-width: 991px) {
              .navbar-4 {
                position: relative !important;
                z-index: 1000 !important;
              }
              .w-nav-overlay {
                top: 100% !important;
                width: 100% !important;
                height: auto !important;
                max-height: calc(100vh - 75px) !important;
                overflow-y: auto !important;
                -webkit-overflow-scrolling: touch !important;
                box-shadow: 0 16px 36px rgba(0, 0, 0, 0.14) !important;
                border-bottom-left-radius: 16px !important;
                border-bottom-right-radius: 16px !important;
                background-color: #ffffff !important;
                z-index: 999 !important;
              }
              .w-nav-overlay .nav-menu-3,
              .nav-menu-3[data-nav-menu-open] {
                display: flex !important;
                flex-direction: column !important;
                align-items: stretch !important;
                justify-content: flex-start !important;
                position: static !important;
                top: 0 !important;
                transform: none !important;
                width: 100% !important;
                height: auto !important;
                max-height: none !important;
                box-shadow: none !important;
                border-radius: 0 !important;
                padding: 10px 0 20px 0 !important;
                background-color: #ffffff !important;
              }
            }
          \`;
          document.head.appendChild(style);
        })()
      `
    });

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
    console.log('Button center at:', x, y);

    // Perform phone tap (touchStart + touchEnd)
    console.log('Dispatching touchStart & touchEnd...');
    await send('Input.dispatchTouchEvent', {
      type: 'touchStart',
      touchPoints: [{ x, y }]
    });
    await new Promise(r => setTimeout(r, 80));
    await send('Input.dispatchTouchEvent', {
      type: 'touchEnd',
      touchPoints: []
    });

    // Wait 300ms
    await new Promise(r => setTimeout(r, 300));

    const check1 = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const btn = document.querySelector('.menu-button-4');
          const menu = document.querySelector('.nav-menu-3');
          const overlay = document.querySelector('.w-nav-overlay');
          const mRect = menu ? menu.getBoundingClientRect() : null;
          const oRect = overlay ? overlay.getBoundingClientRect() : null;
          return {
            btnClasses: btn ? btn.className : null,
            menuDisplay: menu ? window.getComputedStyle(menu).display : null,
            menuRect: mRect ? { top: mRect.top, left: mRect.left, width: mRect.width, height: mRect.height } : null,
            overlayRect: oRect ? { top: oRect.top, left: oRect.left, width: oRect.width, height: oRect.height, display: window.getComputedStyle(overlay).display } : null
          };
        })()
      `,
      returnByValue: true
    });
    console.log('After touch open check:', JSON.stringify(check1.result.value, null, 2));

    // Capture screenshot
    const ss1 = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync('/Users/fanssimarketingdigital/.gemini/antigravity/brain/ae798c42-e236-4a06-8dde-1e2e064fe54e/scratch/local_touch_open.png', Buffer.from(ss1.data, 'base64'));
    console.log('Saved screenshot to scratch/local_touch_open.png');

    // Tap again to close
    console.log('Dispatching second tap to close...');
    await send('Input.dispatchTouchEvent', {
      type: 'touchStart',
      touchPoints: [{ x, y }]
    });
    await new Promise(r => setTimeout(r, 80));
    await send('Input.dispatchTouchEvent', {
      type: 'touchEnd',
      touchPoints: []
    });

    await new Promise(r => setTimeout(r, 400));
    const check2 = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const btn = document.querySelector('.menu-button-4');
          const menu = document.querySelector('.nav-menu-3');
          const overlay = document.querySelector('.w-nav-overlay');
          return {
            btnClasses: btn ? btn.className : null,
            menuDisplay: menu ? window.getComputedStyle(menu).display : null,
            overlayDisplay: overlay ? window.getComputedStyle(overlay).display : null
          };
        })()
      `,
      returnByValue: true
    });
    console.log('After close check:', check2.result.value);

    const ss2 = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync('/Users/fanssimarketingdigital/.gemini/antigravity/brain/ae798c42-e236-4a06-8dde-1e2e064fe54e/scratch/local_touch_closed.png', Buffer.from(ss2.data, 'base64'));
    console.log('Saved screenshot to scratch/local_touch_closed.png');

  } catch (err) {
    console.error('Test error:', err);
  } finally {
    chromeProcess.kill();
    process.exit(0);
  }
}

testTouchOnLocal();
