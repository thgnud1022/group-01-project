import puppeteer from 'puppeteer-core';

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

async function debugDom() {
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1200,1000']
  });
  const page = await browser.newPage();
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2' });

  // Login
  const isLoginPage = await page.$('[data-testid="input-email"]');
  if (isLoginPage) {
    await page.click('[data-testid="test-acc-procurement"]');
    await page.waitForFunction(() => {
      const el = document.querySelector('[data-testid="input-email"]');
      return el && el.value.includes('procurement@company.com');
    });
    await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/auth/me'), { timeout: 15000 }),
      page.click('[data-testid="login-submit-button"]')
    ]);
  }
  await page.waitForSelector('[data-testid="app-shell"]', { timeout: 15000 });

  // Navigate to Sourcing
  await page.click('[data-testid="nav-sourcing"]');
  await page.waitForFunction(() => !document.querySelector('[data-testid="sourcing-loading"]'), { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1000));

  const testIds = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('[data-testid]')).map(el => el.getAttribute('data-testid'));
  });
  console.log('Found testids in DOM:', testIds);

  const texts = await page.evaluate(() => document.body.innerText);
  console.log('Page text snippet:\n', texts.slice(0, 800));

  await browser.close();
}

debugDom();
