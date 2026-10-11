const { spawn } = require('child_process');
const fs = require('fs');

async function testDesktop() {
  const chromeProcess = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
    '--headless=new',
    '--remote-debugging-port=9229',
    '--user-data-dir=/tmp/chrome_desktop_' + Date.now(),
    '--no-first-run',
    '--no-default-browser-check'
  ]);

  await new Promise(r => setTimeout(r, 1200));

  try {
    const listRes = await fetch('http://127.0.0.1:9229/json/list');
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
      width: 1440,
      height: 900,
      deviceScaleFactor: 1,
      mobile: false
    });

    console.log('Navigating to LIVE Desktop...');
    await send('Page.navigate', { url: 'https://oncologia-robotica.com/?v=' + Date.now() });
    await new Promise(r => setTimeout(r, 3000));

    const desktopCheck = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const btn = document.querySelector('.menu-button-4');
          const menu = document.querySelector('.nav-menu-3');
          return {
            btnDisplay: btn ? window.getComputedStyle(btn).display : null,
            menuDisplay: menu ? window.getComputedStyle(menu).display : null
          };
        })()
      `,
      returnByValue: true
    });
    console.log('Desktop Navbar state:', desktopCheck.result.value);

    const ssDesktop = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync('/Users/fanssimarketingdigital/.gemini/antigravity/brain/ae798c42-e236-4a06-8dde-1e2e064fe54e/scratch/live_desktop_verified.png', Buffer.from(ssDesktop.data, 'base64'));
    console.log('Saved desktop screenshot to scratch/live_desktop_verified.png');

  } catch (err) {
    console.error('Desktop test error:', err);
  } finally {
    chromeProcess.kill();
    process.exit(0);
  }
}

testDesktop();
