import puppeteer from 'puppeteer-core';

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

async function testCreatePR() {
  console.log('=== TESTING REAL E2E PR SUBMISSION TO BACKEND ===');
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1181, height: 796 });

  page.on('console', msg => console.log(`[BROWSER] ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`[PAGE ERROR] ${err.message}`));

  await page.goto('http://localhost:5173/');

  // Login as employee
  await page.waitForSelector('[data-testid="input-email"]');
  await page.click('[data-testid="test-acc-employee"]');
  await page.click('[data-testid="login-submit-button"]');
  await page.waitForSelector('[data-testid="app-shell"]');

  // Go to New Request
  await page.evaluate(() => document.querySelector('[data-testid="nav-new-request"]')?.click());
  await page.waitForSelector('[data-testid="new-request-view"]');

  // Fill in form
  console.log('Filling form fields...');
  await page.type('[data-testid="input-request-title"]', 'Dell XPS Laptops for QA Team');
  await page.select('[data-testid="select-category"]', 'IT Equipment');
  await page.select('[data-testid="select-department"]', 'Engineering');
  await page.type('[data-testid="input-cost-centre"]', 'CC-ENG-2200');
  await page.type('[data-testid="input-delivery-location"]', 'HQ Hanoi · Floor 6 · Goods-in');
  await page.type('[data-testid="textarea-justification"]', 'Urgent replenishment for QA automated testing benches.');

  // Fill line item
  await page.type('[data-testid="item-desc-0"]', 'Dell XPS 15 32GB');
  await page.$eval('[data-testid="item-qty-0"]', el => el.value = '');
  await page.type('[data-testid="item-qty-0"]', '2');
  await page.$eval('[data-testid="item-price-0"]', el => el.value = '');
  await page.type('[data-testid="item-price-0"]', '25000000');

  // Submit and wait for POST /api/pr
  console.log('Submitting PR to FastAPI backend...');
  const [prResponse] = await Promise.all([
    page.waitForResponse(res => res.url().includes('/api/pr') && res.request().method() === 'POST', { timeout: 15000 }),
    page.evaluate(() => document.querySelector('[data-testid="submit-for-approval-btn"]')?.click())
  ]);

  console.log(`Backend POST /api/pr HTTP Status: ${prResponse.status()}`);
  const json = await prResponse.json();
  console.log('Created PR Response from PostgreSQL:', json);

  if (prResponse.status() !== 200 && prResponse.status() !== 201) {
    throw new Error(`Failed to create PR: status ${prResponse.status()} - ${JSON.stringify(json)}`);
  }

  console.log(`✓ Real PR Created successfully with ID: ${json.id}`);
  await browser.close();
}

testCreatePR().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
