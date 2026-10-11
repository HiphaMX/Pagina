const { spawn } = require('child_process');
const fs = require('fs');

async function diagnose() {
  const chromeProcess = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
    '--headless=new',
    '--remote-debugging-port=9222',
    '--user-data-dir=/tmp/chrome_diag',
    '--no-first-run',
    '--no-default-browser-check',
    '--window-size=375,667'
  ]);

  await new Promise(r => setTimeout(r, 1500));

  try {
    const listRes = await fetch('http://127.0.0.1:9222/json/list');
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
      width: 375,
      height: 667,
      deviceScaleFactor: 2,
      mobile: true
    });

    await send('Page.navigate', {
      url: 'file:///Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/OncologiaRobotica/index.html'
    });

    await new Promise(r => setTimeout(r, 2000));

    // Apply data-animation="none"
    await send('Runtime.evaluate', {
      expression: `
        (() => {
          const nav = document.querySelector('.navbar-4');
          nav.setAttribute('data-animation', 'none');
          nav.setAttribute('data-duration', '0');

          const style = document.createElement('style');
          style.id = 'debug-style';
          style.textContent = \`
            .w-nav-overlay .nav-menu-3,
            .nav-menu-3[data-nav-menu-open] {
              display: flex !important;
              flex-direction: column !important;
              top: 0 !important;
              position: static !important;
            }
          \`;
          document.head.appendChild(style);
        })()
      `
    });

    // Click menu button
    await send('Runtime.evaluate', {
      expression: `document.querySelector('.menu-button-4').click();`
    });

    await new Promise(r => setTimeout(r, 300));

    const diag = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const menu = document.querySelector('.nav-menu-3');
          const overlay = document.querySelector('.w-nav-overlay');
          const navbar = document.querySelector('.navbar-4');
          const hero = document.querySelector('.hero-section, .hero, section');

          function getInfo(el) {
            if (!el) return null;
            const cs = window.getComputedStyle(el);
            const r = el.getBoundingClientRect();
            return {
              tag: el.tagName,
              class: el.className,
              rect: { top: r.top, left: r.left, width: r.width, height: r.height, bottom: r.bottom },
              zIndex: cs.zIndex,
              position: cs.position,
              display: cs.display,
              visibility: cs.visibility,
              opacity: cs.opacity,
              overflow: cs.overflow,
              background: cs.backgroundColor,
              transform: cs.transform
            };
          }

          const elemAtCenter = document.elementFromPoint(180, 250);

          return {
            navbar: getInfo(navbar),
            overlay: getInfo(overlay),
            menu: getInfo(menu),
            elementUnderNavbar: elemAtCenter ? {
              tag: elemAtCenter.tagName,
              class: elemAtCenter.className,
              id: elemAtCenter.id
            } : null,
            childrenCount: menu.children.length,
            firstChild: menu.children[0] ? getInfo(menu.children[0]) : null
          };
        })()
      `,
      returnByValue: true
    });

    console.log('Diagnostic result:\n', JSON.stringify(diag.result.value, null, 2));

  } catch (err) {
    console.error('Error:', err);
  } finally {
    chromeProcess.kill();
    process.exit(0);
  }
}

diagnose();
