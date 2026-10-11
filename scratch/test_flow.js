const { spawn } = require('child_process');
const fs = require('fs');

async function testFullMobileFlow() {
  const chromeProcess = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
    '--headless=new',
    '--remote-debugging-port=9226',
    '--user-data-dir=/tmp/chrome_test_flow_' + Date.now(),
    '--no-first-run',
    '--no-default-browser-check'
  ]);

  await new Promise(r => setTimeout(r, 1200));

  try {
    const listRes = await fetch('http://127.0.0.1:9226/json/list');
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

    await send('Page.navigate', {
      url: 'file:///Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/OncologiaRobotica/index.html'
    });
    await new Promise(r => setTimeout(r, 2000));

    // Inject the optimized CSS and replace script logic
    await send('Runtime.evaluate', {
      expression: `
        (() => {
          const nav = document.querySelector('.navbar-4');
          nav.setAttribute('data-animation', 'none');
          nav.setAttribute('data-duration', '0');

          const style = document.createElement('style');
          style.textContent = \`
            @media screen and (max-width: 991px) {
              .navbar-4 {
                position: relative !important;
                z-index: 1000 !important;
              }
              .menu-button-4 {
                cursor: pointer !important;
                -webkit-tap-highlight-color: transparent !important;
                touch-action: manipulation !important;
                user-select: none !important;
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
              .w-nav-overlay:not([style*="display: block"]) {
                display: none !important;
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
      // also synthetic mouse click (mimics phone browser)
      await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
      await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
    };

    console.log('1. Tapping menu button to open...');
    await tapSelector('.menu-button-4');
    await new Promise(r => setTimeout(r, 400));

    const checkOpen = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const btn = document.querySelector('.menu-button-4');
          const menu = document.querySelector('.nav-menu-3');
          const r = menu.getBoundingClientRect();
          return {
            isOpen: btn.classList.contains('w--open'),
            display: window.getComputedStyle(menu).display,
            rect: { top: r.top, left: r.left, width: r.width, height: r.height }
          };
        })()
      `,
      returnByValue: true
    });
    console.log('Open state:', checkOpen.result.value);

    // Save screenshot
    const ssOpen = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync('/Users/fanssimarketingdigital/.gemini/antigravity/brain/ae798c42-e236-4a06-8dde-1e2e064fe54e/scratch/flow_1_open.png', Buffer.from(ssOpen.data, 'base64'));

    console.log('2. Tapping DIAGNÓSTICO dropdown toggle...');
    await tapSelector('.dropdown-toggle:nth-of-type(1), .dropdown-2 .dropdown-toggle');
    await new Promise(r => setTimeout(r, 300));

    const ssDiag = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync('/Users/fanssimarketingdigital/.gemini/antigravity/brain/ae798c42-e236-4a06-8dde-1e2e064fe54e/scratch/flow_2_dropdown.png', Buffer.from(ssDiag.data, 'base64'));

    console.log('3. Tapping menu button to close...');
    await tapSelector('.menu-button-4');
    await new Promise(r => setTimeout(r, 400));

    const checkClosed = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const btn = document.querySelector('.menu-button-4');
          const menu = document.querySelector('.nav-menu-3');
          return {
            isOpen: btn.classList.contains('w--open'),
            display: window.getComputedStyle(menu).display
          };
        })()
      `,
      returnByValue: true
    });
    console.log('Closed state:', checkClosed.result.value);

    const ssClosed = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync('/Users/fanssimarketingdigital/.gemini/antigravity/brain/ae798c42-e236-4a06-8dde-1e2e064fe54e/scratch/flow_3_closed.png', Buffer.from(ssClosed.data, 'base64'));

    console.log('All flow tests completed successfully!');

  } catch (err) {
    console.error('Flow test error:', err);
  } finally {
    chromeProcess.kill();
    process.exit(0);
  }
}

testFullMobileFlow();
