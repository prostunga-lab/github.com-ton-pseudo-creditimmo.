// Rend chaque image du Short : node render.js data.json dossier_frames fps durée
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [dataPath, outDir, fps, total] = process.argv.slice(2);
  const data = fs.readFileSync(dataPath, 'utf8');
  const html = fs.readFileSync(path.join(__dirname, JSON.parse(data).format === 'long' ? 'template_long.html' : 'template.html'), 'utf8')
    .replace('<script>', `<script>window.DATA=${data};</script><script>`);
  const page_path = path.join(__dirname, '_page.html');
  fs.writeFileSync(page_path, html);

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: JSON.parse(data).format === 'long' ? { width: 1920, height: 1080 } : { width: 1080, height: 1920 } });
  await page.goto('file://' + page_path);
  await page.waitForLoadState('networkidle');
  const n = Math.ceil(Number(total) * Number(fps));
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => window.render(t), i / Number(fps));
    await page.screenshot({ path: path.join(outDir, `f${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 88 });
  }
  await browser.close();
})();
