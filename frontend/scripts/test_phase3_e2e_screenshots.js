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

async function runPhase3Screenshots() {
  console.log('=== STARTING PHASE 3 AUTOMATED VISUAL QA & SCREENSHOT SUITE ===');

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

  // 1. LOGIN WITH REAL SUPABASE AUTH (Manager)
  const isLoginPage = await page.$('[data-testid="input-email"]');
  if (isLoginPage) {
    console.log('Authenticating as manager@company.com...');
    await safeClick(page, '[data-testid="test-acc-manager"]');
    await page.waitForFunction(() => {
      const el = document.querySelector('[data-testid="input-email"]');
      return el && el.value.includes('manager@company.com');
    });

    await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/auth/me'), { timeout: 15000 }),
      safeClick(page, '[data-testid="login-submit-button"]')
    ]);
  }

  await page.waitForSelector('[data-testid="app-shell"]', { timeout: 15000 });
  console.log('AppShell loaded successfully.');

  // ==========================================
  // STEP 1: APPROVALS QUEUE (Figma 9:1813)
  // ==========================================
  console.log('\n--- VERIFYING STEP 1: APPROVALS QUEUE (9:1813) ---');
  await safeClick(page, '[data-testid="nav-approvals"]');
  await page.waitForSelector('[data-testid="approvals-queue-view"]', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1200));
  await dismissToast(page);

  const step1Path = path.join(EVIDENCE_DIR, 'approvals-queue-browser.png');
  await page.screenshot({ path: step1Path });
  console.log(`✓ Step 1 captured: ${step1Path} (${fs.statSync(step1Path).size} bytes)`);

  // ==========================================
  // STEP 2: APPROVAL + BUDGET WARNING (Figma 9:2010)
  // ==========================================
  console.log('\n--- VERIFYING STEP 2: APPROVAL + BUDGET WARNING (9:2010) ---');
  const reviewCardBtn = await page.$('[data-testid="review-btn-PR-2026-041"]');
  if (reviewCardBtn) {
    await safeClick(page, '[data-testid="review-btn-PR-2026-041"]');
  } else {
    // Fallback: click first review button
    await page.evaluate(() => {
      const btn = document.querySelector('[data-testid^="review-btn-"]');
      if (btn) btn.click();
    });
  }
  await page.waitForSelector('[data-node-id="9:2010"]', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1200));
  await dismissToast(page);

  const step2Path = path.join(EVIDENCE_DIR, 'approval-budget-warning-browser.png');
  await page.screenshot({ path: step2Path });
  console.log(`✓ Step 2 captured: ${step2Path} (${fs.statSync(step2Path).size} bytes)`);

  // ==========================================
  // STEP 3: EDIT LOCKED IN APPROVAL (Figma 9:2321)
  // ==========================================
  console.log('\n--- VERIFYING STEP 3: EDIT LOCKED (9:2321) ---');
  await safeClick(page, '[data-testid="edit-request-top-btn"]');
  await page.waitForSelector('[data-node-id="9:2321"]', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1200));
  await dismissToast(page);

  const step3Path = path.join(EVIDENCE_DIR, 'edit-locked-browser.png');
  await page.screenshot({ path: step3Path });
  console.log(`✓ Step 3 captured: ${step3Path} (${fs.statSync(step3Path).size} bytes)`);

  // Dismiss lock modal
  await safeClick(page, '[data-testid="back-to-request-btn"]');
  await page.waitForSelector('[data-node-id="9:2010"]', { timeout: 15000 });

  // ==========================================
  // STEP 4: BUDGET REVIEW (Figma 9:2431)
  // ==========================================
  console.log('\n--- VERIFYING STEP 4: BUDGET REVIEW (9:2431) ---');
  await safeClick(page, '[data-testid="nav-budget-review"]');
  await page.waitForSelector('[data-node-id="9:2431"]', { timeout: 15000 });
  await page.waitForSelector('[data-testid="budget-lines-table"]', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1200));
  await dismissToast(page);

  const step4Path = path.join(EVIDENCE_DIR, 'budget-review-browser.png');
  await page.screenshot({ path: step4Path });
  console.log(`✓ Step 4 captured: ${step4Path} (${fs.statSync(step4Path).size} bytes)`);

  // ==========================================
  // STEP 5: FINANCE BUDGET DECISION (Figma 9:2635)
  // ==========================================
  console.log('\n--- VERIFYING STEP 5: FINANCE BUDGET DECISION (9:2635) ---');
  await safeClick(page, '[data-testid="review-budget-btn"]');
  await page.waitForSelector('[data-node-id="9:2635"]', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1200));
  await dismissToast(page);

  const step5Path = path.join(EVIDENCE_DIR, 'finance-budget-decision-browser.png');
  await page.screenshot({ path: step5Path });
  console.log(`✓ Step 5 captured: ${step5Path} (${fs.statSync(step5Path).size} bytes)`);

  // Return to Approvals Queue
  await safeClick(page, '[data-testid="back-to-all-requests"]');
  await safeClick(page, '[data-testid="nav-approvals"]');
  await page.waitForSelector('[data-testid="approvals-queue-view"]', { timeout: 15000 });

  // ==========================================
  // STEP 6: REVISION REQUIRED (Figma 9:2928)
  // ==========================================
  console.log('\n--- VERIFYING STEP 6: REVISION REQUIRED (9:2928) ---');
  await safeClick(page, '[data-testid="recent-item-PR-2026-037"]');
  await page.waitForSelector('[data-node-id="9:2928"]', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1200));
  await dismissToast(page);

  const step6Path = path.join(EVIDENCE_DIR, 'revision-required-browser.png');
  await page.screenshot({ path: step6Path });
  console.log(`✓ Step 6 captured: ${step6Path} (${fs.statSync(step6Path).size} bytes)`);

  // ==========================================
  // STEP 7: EDIT AFTER REVISION (Figma 9:3179)
  // ==========================================
  console.log('\n--- VERIFYING STEP 7: EDIT AFTER REVISION (9:3179) ---');
  await safeClick(page, '[data-testid="edit-and-resubmit-btn"]');
  await page.waitForSelector('[data-node-id="9:3179"]', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1200));
  await dismissToast(page);

  const step7Path = path.join(EVIDENCE_DIR, 'edit-after-revision-browser.png');
  await page.screenshot({ path: step7Path });
  console.log(`✓ Step 7 captured: ${step7Path} (${fs.statSync(step7Path).size} bytes)`);

  // Return to Approvals Queue
  await safeClick(page, '[data-testid="back-link"]');
  await safeClick(page, '[data-testid="back-to-all-requests"]');
  await safeClick(page, '[data-testid="nav-approvals"]');
  await page.waitForSelector('[data-testid="approvals-queue-view"]', { timeout: 15000 });

  // ==========================================
  // STEP 8: REJECTED REQUEST (Figma 9:3468)
  // ==========================================
  console.log('\n--- VERIFYING STEP 8: REJECTED REQUEST (9:3468) ---');
  await safeClick(page, '[data-testid="recent-item-PR-2026-036"]');
  await page.waitForSelector('[data-node-id="9:3468"]', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1200));
  await dismissToast(page);

  const step8Path = path.join(EVIDENCE_DIR, 'rejected-request-browser.png');
  await page.screenshot({ path: step8Path });
  console.log(`✓ Step 8 captured: ${step8Path} (${fs.statSync(step8Path).size} bytes)`);

  // Return to Approvals Queue
  await safeClick(page, '[data-testid="back-to-all-requests"]');
  await safeClick(page, '[data-testid="nav-approvals"]');
  await page.waitForSelector('[data-testid="approvals-queue-view"]', { timeout: 15000 });

  // ==========================================
  // STEP 9: APPROVED REQUEST (Figma 9:3745)
  // ==========================================
  console.log('\n--- VERIFYING STEP 9: APPROVED REQUEST (9:3745) ---');
  // Click on the approved item
  const recentApprovedBtn = await page.$('[data-testid="recent-item-PR-2026-040"]');
  if (recentApprovedBtn) {
    await safeClick(page, '[data-testid="recent-item-PR-2026-040"]');
  } else {
    await safeClick(page, '[data-testid^="recent-item-"]');
  }
  await page.waitForSelector('[data-node-id="9:3745"]', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1200));
  await dismissToast(page);

  const step9Path = path.join(EVIDENCE_DIR, 'approved-request-browser.png');
  await page.screenshot({ path: step9Path });
  console.log(`✓ Step 9 captured: ${step9Path} (${fs.statSync(step9Path).size} bytes)`);

  await browser.close();
  console.log('\n=== ALL 9 PHASE 3 BROWSER SCREENSHOTS CAPTURED SUCCESSFULLY ===');
}

runPhase3Screenshots().catch(err => {
  console.error('Test Suite Failed:', err);
  process.exit(1);
});
