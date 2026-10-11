const { spawn } = require('child_process');

async function inspectMobileHeader() {
  const chromeProcess = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
    '--headless=new',
    '--remote-debugging-port=9230',
    '--user-data-dir=/tmp/chrome_inspect_header_' + Date.now(),
    '--no-first-run',
    '--no-default-browser-check'
  ]);

  await new Promise(r => setTimeout(r, 1200));

  try {
    const listRes = await fetch('http://127.0.0.1:9230/json/list');
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

    // Emulate iPhone / Android matching user's phone ratio (~390x844)
    await send('Emulation.setDeviceMetricsOverride', {
      width: 390,
      height: 844,
      deviceScaleFactor: 3,
      mobile: true,
      hasTouch: true
    });

    await send('Page.navigate', {
      url: 'file:///Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/OncologiaRobotica/index.html'
    });
    await new Promise(r => setTimeout(r, 2000));

    const analysis = await send('Runtime.evaluate', {
      expression: `
        (() => {
          function inspect(sel) {
            const el = document.querySelector(sel);
            if (!el) return { error: 'not found' };
            const r = el.getBoundingClientRect();
            const cs = window.getComputedStyle(el);
            return {
              tag: el.tagName,
              rect: { top: r.top, bottom: r.bottom, height: r.height, left: r.left, width: r.width },
              margin: \`\${cs.marginTop} \${cs.marginRight} \${cs.marginBottom} \${cs.marginLeft}\`,
              padding: \`\${cs.paddingTop} \${cs.paddingRight} \${cs.paddingBottom} \${cs.paddingLeft}\`,
              display: cs.display,
              position: cs.position,
              height: cs.height,
              minHeight: cs.minHeight
            };
          }

          return {
            body: inspect('body'),
            navbar: inspect('.navbar-4'),
            topBar: inspect('.container-top.top-bar'),
            navbarContainer: inspect('.navbar-container-2'),
            brandMobile: inspect('.brand-mobile'),
            logoImage: inspect('.image-46'),
            menuBtn: inspect('.menu-button-4'),
            heroSection: inspect('.hero-section'),
            hero2: inspect('.hero-2'),
            heroContent: inspect('.hero-content')
          };
        })()
      `,
      returnByValue: true
    });

    console.log(JSON.stringify(analysis.result.value, null, 2));

  } catch (err) {
    console.error(err);
  } finally {
    chromeProcess.kill();
    process.exit(0);
  }
}

inspectMobileHeader();
