import puppeteer from 'puppeteer-core';

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

async function main() {
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
  });
  const page = await browser.newPage();
  page.on('console', msg => console.log('LOG:', msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.message, err.stack));

  await page.goto('http://localhost:5173/');
  await page.waitForSelector('[data-testid="input-email"]');
  await page.click('[data-testid="test-acc-employee"]');
  await page.click('[data-testid="login-submit-button"]');
  await page.waitForSelector('[data-testid="app-shell"]');

  console.log('App shell ready, looking for nav items...');
  const navBtns = await page.$$eval('[data-testid^="nav-"]', els => els.map(e => e.getAttribute('data-testid')));
  console.log('Nav buttons found:', navBtns);

  console.log('Clicking nav-new-request...');
  await page.click('[data-testid="nav-new-request"]');
  await new Promise(r => setTimeout(r, 2000));

  const hasNewReq = await page.$('[data-testid="new-request-view"]');
  console.log('Has new-request-view:', !!hasNewReq);

  const mainHtml = await page.evaluate(() => document.querySelector('main')?.innerHTML || document.body.innerHTML);
  console.log('Main snippet:', mainHtml.slice(0, 300));

  await browser.close();
}

main().catch(console.error);
