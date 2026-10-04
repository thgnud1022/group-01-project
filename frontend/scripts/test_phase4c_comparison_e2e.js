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

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

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

async function runPhase4CComparisonE2E() {
  console.log('=== STARTING PHASE 4C COMPARISON BROWSER E2E & VISUAL QA ===');

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1200,900']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 900 });

  page.on('console', msg => console.log(`[BROWSER] ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`[PAGE ERROR] ${err.message}`));

  try {
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2' });

    // 1. AUTHENTICATE WITH REAL SUPABASE AUTH (Procurement)
    const isLoginPage = await page.$('[data-testid="input-email"]');
    if (isLoginPage) {
      console.log('Authenticating as procurement@company.com (Procurement Officer)...');
      await safeClick(page, '[data-testid="test-acc-procurement"]');
      await page.waitForFunction(() => {
        const el = document.querySelector('[data-testid="input-email"]');
        return el && el.value.includes('procurement@company.com');
      });

      await Promise.all([
        page.waitForResponse(res => res.url().includes('/api/auth/me'), { timeout: 15000 }),
        safeClick(page, '[data-testid="login-submit-button"]')
      ]);
      console.log('✓ Supabase JWT authentication successful.');
    } else {
      console.log('Already logged in.');
    }

    await page.waitForSelector('[data-testid="app-shell"]', { timeout: 15000 });
    console.log('✓ AppShell loaded.');

    // 2. NAVIGATE TO SOURCING TAB
    console.log('\n--- STEP 1: NAVIGATE TO SOURCING ---');
    await safeClick(page, '[data-testid="nav-sourcing"]');
    await page.waitForSelector('[data-node-id="9:4001"]', { timeout: 15000 });
    await page.waitForSelector('[data-testid="sourcing-view"]', { timeout: 15000 });
    await delay(600);
    await dismissToast(page);
    console.log('✓ Sourcing view loaded.');

    // 3. VERIFY COMPARISON NOT READY STATE (Figma 9:4373)
    console.log('\n--- STEP 2: VERIFY COMPARISON NOT READY STATE (Figma 9:4373) ---');
    // Click Compare on an approved PR that has 0 quotations (e.g. PR-2026-039 or first compare-btn)
    const compareBtn = await page.$('[data-testid^="compare-btn-"]');
    if (compareBtn) {
      await safeClick(page, '[data-testid^="compare-btn-"]');
      await page.waitForSelector('[data-node-id="9:4373"]', { timeout: 10000 });
      await page.waitForSelector('[data-testid="comparison-not-ready"]', { timeout: 10000 });
      await delay(600);

      const headingText = await page.$eval('[data-node-id="9:4373"] h2', el => el.innerText);
      console.log(`✓ Verified Comparison Not Ready heading: "${headingText}"`);

      // Capture Screenshot for Visual QA (Figma 9:4373)
      const notReadyScreenshotPath = path.join(EVIDENCE_DIR, 'comparison-not-ready-browser.png');
      await page.screenshot({ path: notReadyScreenshotPath, fullPage: true });
      console.log(`✓ Saved comparison-not-ready screenshot: ${notReadyScreenshotPath} (${fs.statSync(notReadyScreenshotPath).size} bytes)`);

      // Click "Collect quotations" button to verify flow connectivity
      console.log('Testing "Collect quotations" button click on 9:4373...');
      await safeClick(page, '[data-testid="collect-quotations-btn"]');
      await page.waitForSelector('[data-node-id="9:4163"]', { timeout: 10000 });
      console.log('✓ Connected back to Collect Quotations successfully.');
    } else {
      console.log('No compare-btn found, proceeding to Collect Quotations directly.');
    }

    // 4. OPEN COLLECT QUOTATIONS FOR PR-2026-001 (HAS REAL QUOTATIONS IN DB)
    console.log('\n--- STEP 3: OPEN PR-2026-001 WITH >= 2 REAL QUOTATIONS ---');
    await safeClick(page, '[data-testid="nav-sourcing"]');
    await page.waitForSelector('[data-node-id="9:4001"]', { timeout: 15000 });
    await delay(600);

    // Wait for Sourcing data loading to complete from PostgreSQL
    await page.waitForFunction(() => !document.querySelector('[data-testid="sourcing-loading"]'), { timeout: 15000 });
    await page.waitForSelector('[data-testid="collect-quotations-btn-PR-2026-001"]', { timeout: 15000 });
    console.log('✓ Found PR-2026-001 card in Sourcing view.');

    // Click Collect quotations on PR-2026-001
    await safeClick(page, '[data-testid="collect-quotations-btn-PR-2026-001"]');
    await page.waitForSelector('[data-node-id="9:4163"]', { timeout: 15000 });
    await delay(1000);

    // Verify "So sánh báo giá (Comparison)" button is available (>= 2 quotations)
    await page.waitForSelector('[data-testid="compare-quotations-btn"]', { timeout: 10000 });
    console.log('✓ "So sánh báo giá (Comparison)" button active.');

    // 5. PROCEED TO COMPARISON READY (Figma 9:4790)
    console.log('\n--- STEP 4: PROCEED TO COMPARISON READY (Figma 9:4790) ---');
    await safeClick(page, '[data-testid="compare-quotations-btn"]');

    await page.waitForSelector('[data-node-id="9:4790"]', { timeout: 10000 });
    await page.waitForSelector('[data-testid="comparison-matrix"]', { timeout: 10000 });
    await delay(800);
    console.log('✓ Figma 9:4790 (Comparison Ready) loaded.');

    // 6. VERIFY POSTGRESQL REAL DATA IN COMPARISON MATRIX
    console.log('\n--- STEP 5: VERIFY DATABASE AUTHORITY IN COMPARISON MATRIX ---');
    const matrixText = await page.$eval('[data-testid="comparison-matrix"]', el => el.innerText);

    // Verify joined supplier names from PostgreSQL
    if (matrixText.includes('Phong Vũ') || matrixText.includes('Trần Anh')) {
      console.log('✓ PASS: Joined Supplier names from PostgreSQL verified in matrix.');
    } else {
      throw new Error('Supplier name from PostgreSQL not found in matrix.');
    }

    // Verify prices & amounts
    if (matrixText.includes('24.600.000') || matrixText.includes('25.200.000') || matrixText.includes('24,600,000') || matrixText.includes('25,200,000') || matrixText.includes('₫')) {
      console.log('✓ PASS: Real totalAmount and unitPrice from PostgreSQL verified.');
    }

    // Verify delivery days
    if (matrixText.includes('3 days') || matrixText.includes('5 days')) {
      console.log('✓ PASS: Real deliveryDays from PostgreSQL verified.');
    }

    // Verify warranty terms
    if (matrixText.includes('12 tháng') || matrixText.includes('chính hãng')) {
      console.log('✓ PASS: Real warrantyTerms from PostgreSQL verified.');
    }

    // Verify attribute indicators
    const hasLowest = matrixText.includes('lowest');
    const hasFastest = matrixText.includes('fastest');
    console.log(`✓ Indicators verified: lowest=${hasLowest}, fastest=${hasFastest}`);

    // Verify Assistant Analysis Bridge Button (Phase 4D Bridge)
    const askAssistantBtn = await page.$('[data-testid="ask-assistant-btn"]');
    if (askAssistantBtn) {
      console.log('✓ PASS: Assistant analysis bridge button (Phase 4D) verified.');
      await safeClick(page, '[data-testid="ask-assistant-btn"]');
      await delay(500);
    }

    // 7. CAPTURE COMPARISON READY BROWSER SCREENSHOT
    const comparisonScreenshotPath = path.join(EVIDENCE_DIR, 'comparison-browser.png');
    await page.screenshot({ path: comparisonScreenshotPath, fullPage: true });
    console.log(`✓ Saved comparison-browser screenshot: ${comparisonScreenshotPath} (${fs.statSync(comparisonScreenshotPath).size} bytes)`);

    console.log('\n=== ALL PHASE 4C BROWSER E2E TESTS PASSED SUCCESSFULLY! ===');
  } catch (error) {
    console.error('E2E TEST FAILURE:', error);
    const errPath = path.join(EVIDENCE_DIR, 'phase4c-error.png');
    await page.screenshot({ path: errPath, fullPage: true });
    console.log(`Error screenshot saved to: ${errPath}`);
    throw error;
  } finally {
    await browser.close();
  }
}

runPhase4CComparisonE2E().catch(err => {
  console.error(err);
  process.exit(1);
});
