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

async function runPhase2Screenshots() {
  console.log('=== STARTING PHASE 2 AUTOMATED VISUAL QA & SCREENSHOT SUITE ===');

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

  // 1. LOGIN AS EMPLOYEE (Real Supabase Auth)
  const isLoginPage = await page.$('[data-testid="input-email"]');
  if (isLoginPage) {
    console.log('Authenticating as employee@company.com...');
    await safeClick(page, '[data-testid="test-acc-employee"]');
    await page.waitForFunction(() => {
      const el = document.querySelector('[data-testid="input-email"]');
      return el && el.value.includes('employee@company.com');
    });

    await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/auth/me'), { timeout: 15000 }),
      safeClick(page, '[data-testid="login-submit-button"]')
    ]);
  }

  await page.waitForSelector('[data-testid="app-shell"]', { timeout: 15000 });
  console.log('AppShell loaded successfully.');

  // --- STEP 1: PURCHASE REQUESTS LIST (9:317) ---
  console.log('\n--- VERIFYING STEP 1: PURCHASE REQUESTS LIST (9:317) ---');
  await safeClick(page, '[data-testid="nav-purchase-requests"]');
  await page.waitForSelector('[data-testid="purchase-requests-view"]', { timeout: 15000 });
  await page.waitForSelector('[data-testid="pr-table"]', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1200));
  await dismissToast(page);
  
  const step1Path = path.join(EVIDENCE_DIR, 'purchase-requests-browser.png');
  await page.screenshot({ path: step1Path });
  console.log(`✓ Step 1 captured: ${step1Path} (${fs.statSync(step1Path).size} bytes)`);

  // --- STEP 2: NEW REQUEST / FLOW A (9:645) ---
  console.log('\n--- VERIFYING STEP 2: NEW PURCHASE REQUEST (9:645) ---');
  await safeClick(page, '[data-testid="nav-new-request"]');
  await page.waitForSelector('[data-testid="new-request-view"]', { timeout: 15000 });
  await page.waitForSelector('[data-testid="ai-note-input"]', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1200));
  await dismissToast(page);

  const step2Path = path.join(EVIDENCE_DIR, 'new-request-browser.png');
  await page.screenshot({ path: step2Path });
  console.log(`✓ Step 2 captured: ${step2Path} (${fs.statSync(step2Path).size} bytes)`);

  // Interact with suggestions & AI
  console.log('Interacting with suggestions and inputs in New Request...');
  const useCostCentreBtn = await page.$('[data-testid="use-suggestion-costcentre"]');
  if (useCostCentreBtn) {
    await safeClick(page, '[data-testid="use-suggestion-costcentre"]');
  }

  const useLocationBtn = await page.$('[data-testid="use-suggestion-location"]');
  if (useLocationBtn) {
    await safeClick(page, '[data-testid="use-suggestion-location"]');
  }

  // --- STEP 3: DRAFT REQUEST (9:1006) ---
  console.log('\n--- VERIFYING STEP 3: DRAFT PURCHASE REQUEST (9:1006) ---');
  await safeClick(page, '[data-testid="save-as-draft-btn"]');
  await page.waitForSelector('[data-testid="pr-detail-view"]', { timeout: 15000 });
  await page.waitForSelector('[data-testid="continue-editing-btn"]', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1200));
  await dismissToast(page);

  const step3Path = path.join(EVIDENCE_DIR, 'draft-request-browser.png');
  await page.screenshot({ path: step3Path });
  console.log(`✓ Step 3 captured: ${step3Path} (${fs.statSync(step3Path).size} bytes)`);

  // --- STEP 4: EDIT DRAFT REQUEST (9:1237) ---
  console.log('\n--- VERIFYING STEP 4: EDIT DRAFT REQUEST (9:1237) ---');
  await safeClick(page, '[data-testid="continue-editing-btn"]');
  await page.waitForSelector('[data-testid="edit-draft-view"]', { timeout: 15000 });
  await page.waitForSelector('[data-testid="edit-title-input"]', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1200));
  await dismissToast(page);

  const step4Path = path.join(EVIDENCE_DIR, 'edit-draft-browser.png');
  await page.screenshot({ path: step4Path });
  console.log(`✓ Step 4 captured: ${step4Path} (${fs.statSync(step4Path).size} bytes)`);

  // Save changes and return to PR detail
  await safeClick(page, '[data-testid="edit-save-changes-btn"]');
  await page.waitForSelector('[data-testid="pr-detail-view"]', { timeout: 15000 });

  // --- STEP 5: SUBMISSION ERROR STATE (9:1563) ---
  console.log('\n--- VERIFYING STEP 5: SUBMISSION ERROR STATE (9:1563) ---');
  await safeClick(page, '[data-testid="back-to-all-requests"]');
  await page.waitForSelector('[data-testid="purchase-requests-view"]', { timeout: 15000 });

  // Find and click the Error PR: PR-2026-034
  await safeClick(page, '[data-testid="pr-row-PR-2026-034"]');
  await page.waitForSelector('[data-testid="pr-detail-view"]', { timeout: 15000 });
  await page.waitForSelector('[data-testid="retry-submission-btn"]', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1200));
  await dismissToast(page);

  const step5Path = path.join(EVIDENCE_DIR, 'submission-error-browser.png');
  await page.screenshot({ path: step5Path });
  console.log(`✓ Step 5 captured: ${step5Path} (${fs.statSync(step5Path).size} bytes)`);

  // --- STEP 6: PR DETAIL (LIVE REAL PR FROM POSTGRESQL) ---
  console.log('\n--- VERIFYING STEP 6: PR DETAIL (LIVE PR FROM DATABASE) ---');
  await safeClick(page, '[data-testid="back-to-all-requests"]');
  await page.waitForSelector('[data-testid="purchase-requests-view"]', { timeout: 15000 });

  await page.waitForSelector('[data-testid^="pr-row-"]', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1000));

  // Click on the first row
  const firstRow = await page.$('[data-testid^="pr-row-"]');
  if (firstRow) {
    await page.evaluate(el => el.click(), firstRow);
    await page.waitForSelector('[data-testid="pr-detail-view"]', { timeout: 15000 });
    await new Promise(r => setTimeout(r, 1200));
    await dismissToast(page);
    const step6Path = path.join(EVIDENCE_DIR, 'pr-detail-browser.png');
    await page.screenshot({ path: step6Path });
    console.log(`✓ Step 6 captured: ${step6Path} (${fs.statSync(step6Path).size} bytes)`);
  }

  await browser.close();
  console.log('\n=== ALL PHASE 2 SCREENSHOTS CAPTURED SUCCESSFULLY ===');
}

runPhase2Screenshots().catch(err => {
  console.error('Phase 2 screenshot execution failed:', err);
  process.exit(1);
});
