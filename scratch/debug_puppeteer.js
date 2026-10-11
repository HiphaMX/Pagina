
const puppeteer = require('puppeteer');
(async () => {
    const browser = await puppeteer.launch({headless: 'new', args: ['--no-sandbox']});
    const page = await browser.newPage();
    await page.setViewport({width: 390, height: 844});
    await page.goto('http://localhost:8899/index.html', {waitUntil: 'networkidle2'});
    
    // Click menu button
    await page.click('.menu-button-4');
    await new Promise(r => setTimeout(r, 600));
    
    const info = await page.evaluate(() => {
        const res = {};
        const q = (sel) => {
            const el = document.querySelector(sel);
            if (!el) return null;
            const r = el.getBoundingClientRect();
            const cs = window.getComputedStyle(el);
            return {
                rect: {x: r.x, y: r.y, width: r.width, height: r.height},
                display: cs.display,
                width: cs.width,
                flexDirection: cs.flexDirection,
                justifyContent: cs.justifyContent,
                alignItems: cs.alignItems,
                padding: cs.padding,
                margin: cs.margin,
                transform: cs.transform
            };
        };
        res.navbar = q('.navbar-4');
        res.container = q('.navbar-container-2');
        res.menu = q('.nav-menu-3');
        res.colLeft = q('.nav-column.left');
        res.colCenter = q('.nav-column-center');
        res.colRight = q('.nav-column.right');
        res.dropdown = q('.dropdown-2');
        res.toggle = q('.dropdown-toggle');
        res.arrow = q('.dropdown-arrow-2');
        res.text = q('.text-block-13');
        return res;
    });
    console.log(JSON.stringify(info, null, 2));
    await page.screenshot({path: 'scratch/debug_menu_open.png'});
    await browser.close();
})();
