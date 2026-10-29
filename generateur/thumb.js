// Miniature YouTube 1280x720 : node thumb.js <image_fond> <ligne1> <ligne2> <badge> <sortie.png>
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [bg, l1, l2, badge, out] = process.argv.slice(2);
  const svg = fs.readFileSync(path.join(__dirname, 'avatar.svg'), 'utf8');
  const html = `<html><body style="margin:0;width:1280px;height:720px;overflow:hidden;font-family:'DejaVu Sans',Arial;position:relative">
  <div style="position:absolute;inset:0;background:url(${bg}) center/cover;filter:saturate(1.3) contrast(1.1)"></div>
  <div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(20,8,10,.92) 0%,rgba(20,8,10,.6) 55%,rgba(20,8,10,.1) 100%)"></div>
  <div style="position:absolute;left:50px;top:60px;background:#e0262f;color:#fff;font-weight:800;font-size:40px;padding:10px 22px;border-radius:12px;transform:rotate(-3deg)">${badge}</div>
  <div style="position:absolute;left:50px;top:170px;width:820px;color:#fff;font-weight:900;font-size:108px;line-height:1;text-transform:uppercase;-webkit-text-stroke:3px #000;paint-order:stroke fill;text-shadow:0 8px 0 #000">${l1}</div>
  <div style="position:absolute;left:50px;top:420px;width:820px;color:#f2c14e;font-weight:900;font-size:80px;line-height:1.05;-webkit-text-stroke:3px #000;paint-order:stroke fill;text-shadow:0 6px 0 #000">${l2}</div>
  <div style="position:absolute;right:30px;bottom:10px;width:380px;transform:rotate(6deg)">${svg.replace('width="400" height="440"','width="380" height="418"')}</div>
  <div style="position:absolute;right:40px;top:40px;display:flex;height:50px;border-radius:6px;overflow:hidden"><i style="width:25px;background:#1d1d1b"></i><i style="width:25px;background:#f6d02f"></i><i style="width:25px;background:#e0262f"></i></div>
  </body></html>`;
  fs.writeFileSync(path.join(__dirname, '_thumb.html'), html);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  await p.goto('file://' + path.join(__dirname, '_thumb.html')); await p.waitForLoadState('networkidle');
  await p.screenshot({ path: out }); await b.close();
})();
