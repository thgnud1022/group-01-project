import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

async function main() {
  console.log('--- CAPTURING STEP 1: PURCHASE REQUESTS VIEW (9:317) ---');
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1181,796']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1181, height: 796 });

  page.on('console', msg => console.log(`[BROWSER] ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`[PAGE ERROR] ${err.message}`));

  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2' });

  // Check if login needed
  const isLoginPage = await page.$('[data-testid="input-email"]');
  if (isLoginPage) {
    console.log('Logging in as employee...');
    await page.click('[data-testid="test-acc-employee"]');
    await page.waitForFunction(() => {
      const el = document.querySelector('[data-testid="input-email"]');
      return el && el.value.includes('employee@company.com');
    });

    await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/auth/me'), { timeout: 15000 }),
      page.click('[data-testid="login-submit-button"]')
    ]);
  }

  // Wait for AppShell and PurchaseRequestsView
  await page.waitForSelector('[data-testid="purchase-requests-view"]', { timeout: 10000 });
  await page.waitForSelector('[data-testid="pr-table"]', { timeout: 10000 });

  // Allow layout and font rendering
  await new Promise(r => setTimeout(r, 1500));

  const outPath = path.resolve('../docs/evidence/browser/purchase-requests-browser.png');
  await page.screenshot({ path: outPath, fullPage: false });
  console.log(`Saved screenshot to: ${outPath} (${fs.statSync(outPath).size} bytes)`);

  await browser.close();
  console.log('STEP 1 SCREENSHOT CAPTURED SUCCESSFULLY');
}

main().catch(err => {
  console.error('Error running Step 1 screenshot:', err);
  process.exit(1);
});
