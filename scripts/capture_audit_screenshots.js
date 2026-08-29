import { chromium } from '../apps/web/node_modules/playwright/index.mjs';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';


const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const OUTPUT_DIR = path.resolve(__dirname, '../audit/screenshots');
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

const THEMES = ['emerald', 'retro', 'dark', 'night', 'coffee', 'winter', 'corporate', 'light'];

const VIEWPORTS = [
  { name: 'desktop', width: 1706, height: 960 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'mobile', width: 390, height: 844 },
];

async function capture() {
  console.log('🚀 Launching Chrome (/usr/bin/google-chrome-stable) for visual audit capture...');
  const browser = await chromium.launch({ 
    headless: true,
    executablePath: '/usr/bin/google-chrome-stable',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });


  for (const vp of VIEWPORTS) {
    console.log(`\n📸 Capturing viewport: ${vp.name} (${vp.width}x${vp.height})...`);
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      deviceScaleFactor: 2,
    });

    const page = await context.newPage();

    // 1. Capture All 8 Themes on Search Result Page
    for (const theme of THEMES) {
      const url = `http://127.0.0.1:4321/search?q=%D8%B5%D8%AD%D9%8A%D8%AD+%D8%A7%D9%84%D8%A8%D8%AE%D8%A7%D8%B1%D9%8A`;
      try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
        await page.evaluate((th) => {
          document.documentElement.setAttribute('data-theme', th);
          localStorage.setItem('openbayan_theme', th);
        }, theme);
        await page.waitForTimeout(500);

        const filename = `${vp.name}_search_${theme}.png`;
        await page.screenshot({ path: path.join(OUTPUT_DIR, filename), fullPage: false });
        console.log(`  ✓ Saved: ${filename}`);
      } catch (err) {
        console.error(`  ✗ Failed ${theme} on ${vp.name}:`, err.message);
      }
    }

    // 2. Capture Empty State with Actionable Recovery
    try {
      const emptyUrl = `http://127.0.0.1:4321/search?q=%D9%83%D9%84%D9%85%D8%A9_%D8%BA%D9%8A%D8%B1_%D9%85%D9%88%D8%AC%D9%88%D8%AF%D8%A9`;
      await page.goto(emptyUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.waitForTimeout(400);
      const filename = `${vp.name}_empty_state.png`;
      await page.screenshot({ path: path.join(OUTPUT_DIR, filename), fullPage: false });
      console.log(`  ✓ Saved: ${filename}`);
    } catch (err) {
      console.error(`  ✗ Failed empty state on ${vp.name}:`, err.message);
    }

    // 3. Capture Permalink Page in Retro Theme (WCAG Title Test)
    try {
      const permalinkUrl = `http://127.0.0.1:4321/p/884`;
      await page.goto(permalinkUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.evaluate(() => {
        document.documentElement.setAttribute('data-theme', 'retro');
      });
      await page.waitForTimeout(400);
      const filename = `${vp.name}_permalink_retro.png`;
      await page.screenshot({ path: path.join(OUTPUT_DIR, filename), fullPage: false });
      console.log(`  ✓ Saved: ${filename}`);
    } catch (err) {
      console.error(`  ✗ Failed permalink on ${vp.name}:`, err.message);
    }

    // 4. Capture Homepage
    try {
      await page.goto(`http://127.0.0.1:4321/`, { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.waitForTimeout(400);
      const filename = `${vp.name}_homepage.png`;
      await page.screenshot({ path: path.join(OUTPUT_DIR, filename), fullPage: false });
      console.log(`  ✓ Saved: ${filename}`);
    } catch (err) {
      console.error(`  ✗ Failed homepage on ${vp.name}:`, err.message);
    }



    await context.close();
  }

  await browser.close();
  console.log(`\n🎉 All visual audit screenshots saved to: ${OUTPUT_DIR}`);
}

capture().catch((e) => {
  console.error('Fatal capture error:', e);
  process.exit(1);
});
