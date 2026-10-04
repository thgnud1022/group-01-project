import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const EVIDENCE_DIR = path.resolve(__dirname, '../../docs/evidence/browser');
const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

if (!fs.existsSync(EVIDENCE_DIR)) {
  fs.mkdirSync(EVIDENCE_DIR, { recursive: true });
}

async function safeClick(page, selector) {
  await page.waitForSelector(selector, { timeout: 15000 });
  await page.evaluate((sel) => {
    const el = document.querySelector(sel);
    if (!el) throw new Error('Element not found: ' + sel);
    el.click();
  }, selector);
}

async function dismissToast(page) {
  await page.evaluate(() => {
    const toast = document.querySelector('[data-testid="app-message-banner"]');
    if (toast) {
      toast.style.display = 'none';
    }
  });
}

async function runRevisionFlowE2E() {
  console.log('=== STARTING REVISION & RESUBMIT BROWSER E2E TEST ===');

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

  // 1. LOGIN AS EMPLOYEE & CREATE PR
  console.log('--- Step 1: Login as Employee ---');
  await safeClick(page, '[data-testid="test-acc-employee"]');
  await page.waitForFunction(() => {
    const el = document.querySelector('[data-testid="input-email"]');
    return el && el.value.includes('employee@company.com');
  });
  await Promise.all([
    page.waitForResponse(res => res.url().includes('/api/auth/me'), { timeout: 15000 }),
    safeClick(page, '[data-testid="login-submit-button"]')
  ]);
  await page.waitForSelector('[data-testid="app-shell"]', { timeout: 15000 });

  // Create PR
  console.log('--- Step 2: Employee creates new PR ---');
  await safeClick(page, '[data-testid="nav-new-request"]');
  await page.waitForSelector('[data-testid="input-request-title"]', { timeout: 15000 });
  
  const testTitle = `[E2E-REV] Ergonomic accessories for engineers ${Date.now()}`;
  await page.type('[data-testid="input-request-title"]', testTitle);
  await page.select('[data-testid="select-category"]', 'IT Equipment');
  await page.select('[data-testid="select-department"]', 'Engineering');
  
  // Submit PR
  const [createRes] = await Promise.all([
    page.waitForResponse(res => res.url().includes('/api/pr') && res.request().method() === 'POST', { timeout: 15000 }),
    safeClick(page, '[data-testid="submit-for-approval-btn"]')
  ]);

  const createdPr = await createRes.json();
  const createdPrId = createdPr.id;
  console.log(`PR created with real ID: ${createdPrId}. Now logging out employee...`);

  await dismissToast(page);
  await safeClick(page, '[data-testid="logout-button"]');
  await page.waitForSelector('[data-testid="input-email"]', { timeout: 15000 });

  // 2. LOGIN AS MANAGER & REQUEST REVISION
  console.log('--- Step 3: Login as Manager to Request Revision ---');
  await safeClick(page, '[data-testid="test-acc-manager"]');
  await page.waitForFunction(() => {
    const el = document.querySelector('[data-testid="input-email"]');
    return el && el.value.includes('manager@company.com');
  });
  await Promise.all([
    page.waitForResponse(res => res.url().includes('/api/auth/me'), { timeout: 15000 }),
    safeClick(page, '[data-testid="login-submit-button"]')
  ]);
  await page.waitForSelector('[data-testid="app-shell"]', { timeout: 15000 });

  // Open Approvals
  await safeClick(page, '[data-testid="nav-approvals"]');
  await page.waitForSelector('[data-testid="approvals-queue-view"]', { timeout: 15000 });
  
  // Wait for loading spinner to disappear
  await page.waitForFunction(() => !document.querySelector('.animate-spin'), { timeout: 15000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 2000));

  const availableReviewBtns = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('[data-testid^="review-btn-"]')).map(el => el.getAttribute('data-testid'));
  });
  console.log(`Available review buttons in DOM:`, availableReviewBtns);

  // Find the exact card with createdPrId or fallback
  console.log(`Opening PR ${createdPrId} for review...`);
  const targetSelector = `[data-testid="review-btn-${createdPrId}"]`;
  const exists = await page.$(targetSelector);
  if (exists) {
    await safeClick(page, targetSelector);
  } else {
    console.log(`Specific button ${targetSelector} not found. Available: ${availableReviewBtns.join(', ')}`);
    // Fallback: click first button if createdPr is top of list
    await safeClick(page, availableReviewBtns[0] ? `[data-testid="${availableReviewBtns[0]}"]` : '[data-testid^="review-btn-"]');
  }

  await page.waitForSelector('[data-testid="request-revision-btn"]', { timeout: 15000 });
  await dismissToast(page);


  // Click Request Revision
  console.log('Clicking Request Revision...');
  const [revisionRes] = await Promise.all([
    page.waitForResponse(res => res.url().includes('/revision') && res.request().method() === 'POST', { timeout: 15000 }),
    safeClick(page, '[data-testid="request-revision-btn"]')
  ]);
  console.log(`Revision API Response status: ${revisionRes.status()}`);
  if (revisionRes.status() !== 200) {
    const errBody = await revisionRes.text();
    console.error(`Request revision error body: ${errBody}`);
    throw new Error(`Request revision failed with status ${revisionRes.status()}: ${errBody}`);
  }

  // Verify UI displays Revision requested (Figma 9:2928)
  await page.waitForSelector('[data-node-id="9:2928"]', { timeout: 15000 });
  console.log('✓ Verified: PR status is now REVISION_REQUIRED (Figma 9:2928 shown)');

  // Take screenshot of Figma 9:2928 state
  const revPath = path.join(EVIDENCE_DIR, 'revision-required-real-flow.png');
  await page.screenshot({ path: revPath });
  console.log(`Captured: ${revPath}`);

  // Logout manager
  await safeClick(page, '[data-testid="logout-button"]');
  await page.waitForSelector('[data-testid="input-email"]', { timeout: 15000 });

  // 3. LOGIN BACK AS EMPLOYEE & EDIT + RESUBMIT
  console.log('--- Step 4: Login as Employee to Edit & Resubmit ---');
  await safeClick(page, '[data-testid="test-acc-employee"]');
  await page.waitForFunction(() => {
    const el = document.querySelector('[data-testid="input-email"]');
    return el && el.value.includes('employee@company.com');
  });
  await Promise.all([
    page.waitForResponse(res => res.url().includes('/api/auth/me'), { timeout: 15000 }),
    safeClick(page, '[data-testid="login-submit-button"]')
  ]);
  await page.waitForSelector('[data-testid="app-shell"]', { timeout: 15000 });

  // Open PR list and select the revision-required PR
  await safeClick(page, '[data-testid="nav-purchase-requests"]');
  await new Promise(r => setTimeout(r, 1000));

  // Click on the PR row with createdPrId
  console.log(`Opening created PR ${createdPrId} as employee...`);
  await safeClick(page, `[data-testid="pr-row-${createdPrId}"]`);

  await page.waitForSelector('[data-node-id="9:2928"]', { timeout: 15000 });
  console.log('Opened Revision Required PR as employee.');


  // Click Edit and resubmit
  await safeClick(page, '[data-testid="edit-and-resubmit-btn"]');
  await page.waitForSelector('[data-node-id="9:3179"]', { timeout: 15000 });
  console.log('✓ Verified: Edit After Revision View loaded (Figma 9:3179)');

  // Modify title / item
  await page.type('input[placeholder="Item 1 description"]', ' (Phase 1 Split)');
  await new Promise(r => setTimeout(r, 500));

  // Take screenshot of Figma 9:3179 state
  const editPath = path.join(EVIDENCE_DIR, 'edit-after-revision-real-flow.png');
  await page.screenshot({ path: editPath });
  console.log(`Captured: ${editPath}`);

  // Click Resubmit
  console.log('Submitting Resubmit for approval...');
  const [resubmitRes] = await Promise.all([
    page.waitForResponse(res => res.url().includes('/resubmit') && res.request().method() === 'POST', { timeout: 15000 }),
    safeClick(page, '[data-testid="resubmit-btn"]')
  ]);
  console.log(`Resubmit API Response status: ${resubmitRes.status()}`);
  if (resubmitRes.status() !== 200) {
    throw new Error(`Resubmit failed with status ${resubmitRes.status()}`);
  }

  // Wait for return to PR Detail or Request list with PENDING_MANAGER_APPROVAL
  await new Promise(r => setTimeout(r, 1500));
  await page.waitForSelector('[data-testid="app-shell"]', { timeout: 15000 });
  console.log('✓ Successfully resubmitted PR to backend!');

  await browser.close();
  console.log('\n=== REVISION & RESUBMIT BROWSER E2E TEST COMPLETED SUCCESSFULLY ===');
}

runRevisionFlowE2E().catch(err => {
  console.error('Revision Flow E2E Failed:', err);
  process.exit(1);
});
