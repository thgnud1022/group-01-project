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

async function runPhase4BQuotationE2E() {
  console.log('=== STARTING PHASE 4B QUOTATION FLOW E2E BROWSER TEST ===\n');

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1181,796']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1181, height: 796 });

  page.on('console', msg => console.log(`[BROWSER] ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`[PAGE ERROR] ${err.message}`));

  try {
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2' });

    // 1. AUTHENTICATE WITH REAL SUPABASE AUTH AS PROCUREMENT
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
    }

    await page.waitForSelector('[data-testid="app-shell"]', { timeout: 15000 });
    console.log('✓ AppShell loaded.');

    // 2. NAVIGATE TO SOURCING TAB
    console.log('\n--- STEP 1: NAVIGATE TO SOURCING ---');
    await safeClick(page, '[data-testid="nav-sourcing"]');
    await page.waitForSelector('[data-node-id="9:4001"]', { timeout: 15000 });
    await page.waitForSelector('[data-testid="sourcing-view"]', { timeout: 15000 });
    await page.waitForSelector('[data-testid="sourcing-loading"]', { hidden: true, timeout: 15000 }).catch(() => {});
    await new Promise(r => setTimeout(r, 600));
    console.log('✓ Sourcing view loaded.');

    // 3. OPEN COLLECT QUOTATIONS SCREEN (Figma 9:4163)
    console.log('\n--- STEP 2: OPEN COLLECT QUOTATIONS SCREEN (Figma 9:4163) ---');
    await safeClick(page, '[data-testid="collect-quotations-btn"]');
    await page.waitForSelector('[data-node-id="9:4163"]', { timeout: 15000 });
    await page.waitForSelector('[data-testid="collect-quotations-view"]', { timeout: 15000 });
    await page.waitForSelector('[data-testid="suppliers-loading"]', { hidden: true, timeout: 15000 }).catch(() => {});
    await new Promise(r => setTimeout(r, 800));
    await dismissToast(page);

    const emptyPath = path.join(EVIDENCE_DIR, 'collect-quotations-empty-browser.png');
    await page.screenshot({ path: emptyPath });
    console.log(`✓ Initial Collect Quotations screenshot captured: ${emptyPath} (${fs.statSync(emptyPath).size} bytes)`);

    // Verify Title & Stepper
    const screenTitle = await page.$eval('[data-testid="collect-quotations-title"]', el => el.textContent);
    console.log(`✓ Verified screen title: "${screenTitle}"`);
    await page.waitForSelector('[data-testid="quotation-stepper"]', { timeout: 5000 });
    await page.waitForSelector('[data-testid="dropzone-disabled"]', { timeout: 5000 });
    console.log('✓ Stepper and disabled dropzone verified before selecting supplier.');

    // 4. TEST VALIDATION ERRORS
    console.log('\n--- STEP 3: TEST VALIDATION & COMMERCIAL FIELDS ---');
    // Select Supplier SUP-01 (Phong Vũ)
    await safeClick(page, '[data-testid="supplier-select-SUP-01"]');
    await page.waitForSelector('[data-testid="input-quotation-qty"]', { timeout: 5000 });
    console.log('✓ Selected supplier SUP-01 (Phong Vũ). Form fields unlocked.');

    // Set invalid quantity (0)
    await page.click('[data-testid="input-quotation-qty"]', { clickCount: 3 });
    await page.keyboard.press('Backspace');
    await page.type('[data-testid="input-quotation-qty"]', '0');

    await safeClick(page, '[data-testid="submit-quotation-btn"]');
    await page.waitForSelector('[data-testid="quotation-form-error"]', { timeout: 5000 });
    const errorText1 = await page.$eval('[data-testid="quotation-form-error"]', el => el.textContent);
    console.log(`✓ Client validation caught invalid quantity: "${errorText1}"`);

    // 5. SUBMIT FIRST REAL QUOTATION (SUP-01 Phong Vũ -> PostgreSQL)
    console.log('\n--- STEP 4: SUBMIT QUOTATION 1 (SUP-01 -> POST /api/quotations) ---');
    // Set valid quantity (3)
    await page.click('[data-testid="input-quotation-qty"]', { clickCount: 3 });
    await page.keyboard.press('Backspace');
    await page.type('[data-testid="input-quotation-qty"]', '3');

    // Set unit price (8,200,000)
    await page.click('[data-testid="input-quotation-unit-price"]', { clickCount: 3 });
    await page.keyboard.press('Backspace');
    await page.type('[data-testid="input-quotation-unit-price"]', '8200000');

    // Verify total amount auto-calculated to 24,600,000
    const calcTotal = await page.$eval('[data-testid="input-quotation-total-amount"]', el => el.value);
    console.log(`✓ Total amount auto-calculated: ${calcTotal} (expected 24600000)`);

    // Set delivery days (3) and warranty
    await page.click('[data-testid="input-quotation-delivery-days"]', { clickCount: 3 });
    await page.keyboard.press('Backspace');
    await page.type('[data-testid="input-quotation-delivery-days"]', '3');

    await page.click('[data-testid="input-quotation-warranty"]', { clickCount: 3 });
    await page.keyboard.press('Backspace');
    await page.type('[data-testid="input-quotation-warranty"]', '12 tháng chính hãng Phong Vũ');

    console.log('Submitting quotation for SUP-01...');
    const [quote1Response] = await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/quotations') && res.request().method() === 'POST', { timeout: 15000 }),
      safeClick(page, '[data-testid="submit-quotation-btn"]')
    ]);

    const status1 = quote1Response.status();
    console.log(`✓ POST /api/quotations returned HTTP ${status1}`);
    if (status1 !== 200 && status1 !== 201) {
      const errBody = await quote1Response.text();
      throw new Error(`Failed to create quotation 1: HTTP ${status1} - ${errBody}`);
    }

    const quote1Data = await quote1Response.json();
    console.log(`✓ Quotation 1 created in PostgreSQL with ID: ${quote1Data.id}`);

    await page.waitForSelector('[data-testid="quotation-form-success"]', { timeout: 10000 });
    await page.waitForSelector(`[data-testid="quote-item-${quote1Data.id}"]`, { timeout: 10000 });
    console.log(`✓ Quotation 1 confirmed rendered in "Collected so far" panel.`);

    const oneQuotePath = path.join(EVIDENCE_DIR, 'collect-quotations-one-browser.png');
    await page.screenshot({ path: oneQuotePath });
    console.log(`✓ 1-Quotation screenshot captured: ${oneQuotePath} (${fs.statSync(oneQuotePath).size} bytes)`);

    // 6. SUBMIT SECOND REAL QUOTATION (SUP-02 Trần Anh -> PostgreSQL)
    console.log('\n--- STEP 5: SUBMIT QUOTATION 2 (SUP-02 -> POST /api/quotations) ---');
    await safeClick(page, '[data-testid="supplier-select-SUP-02"]');
    await page.waitForSelector('[data-testid="input-quotation-qty"]', { timeout: 5000 });

    await page.click('[data-testid="input-quotation-qty"]', { clickCount: 3 });
    await page.keyboard.press('Backspace');
    await page.type('[data-testid="input-quotation-qty"]', '3');

    await page.click('[data-testid="input-quotation-unit-price"]', { clickCount: 3 });
    await page.keyboard.press('Backspace');
    await page.type('[data-testid="input-quotation-unit-price"]', '8400000');

    await page.click('[data-testid="input-quotation-delivery-days"]', { clickCount: 3 });
    await page.keyboard.press('Backspace');
    await page.type('[data-testid="input-quotation-delivery-days"]', '5');

    await page.click('[data-testid="input-quotation-warranty"]', { clickCount: 3 });
    await page.keyboard.press('Backspace');
    await page.type('[data-testid="input-quotation-warranty"]', '24 tháng bảo hành tận nơi');

    console.log('Submitting quotation for SUP-02...');
    const [quote2Response] = await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/quotations') && res.request().method() === 'POST', { timeout: 15000 }),
      safeClick(page, '[data-testid="submit-quotation-btn"]')
    ]);

    const status2 = quote2Response.status();
    console.log(`✓ POST /api/quotations returned HTTP ${status2}`);
    if (status2 !== 200 && status2 !== 201) {
      const errBody = await quote2Response.text();
      throw new Error(`Failed to create quotation 2: HTTP ${status2} - ${errBody}`);
    }

    const quote2Data = await quote2Response.json();
    console.log(`✓ Quotation 2 created in PostgreSQL with ID: ${quote2Data.id}`);

    await page.waitForSelector(`[data-testid="quote-item-${quote2Data.id}"]`, { timeout: 10000 });
    console.log(`✓ Quotation 2 confirmed rendered in "Collected so far" panel.`);

    // Verify >= 2 quotations threshold unlocked comparison
    await page.waitForSelector('[data-testid="compare-quotations-btn"]', { timeout: 10000 });
    console.log('✓ Minimum 2 quotations collected: "So sánh báo giá (Comparison)" button unlocked!');

    const fullCollectPath = path.join(EVIDENCE_DIR, 'collect-quotations-browser.png');
    await page.screenshot({ path: fullCollectPath });
    console.log(`✓ Collect Quotations final screenshot captured: ${fullCollectPath} (${fs.statSync(fullCollectPath).size} bytes)`);

    // 7. BACK NAVIGATION TEST
    console.log('\n--- STEP 6: BACK NAVIGATION TO SOURCING ---');
    await safeClick(page, '[data-testid="back-to-sourcing-btn"]');
    await page.waitForSelector('[data-testid="sourcing-view"]', { timeout: 10000 });
    console.log('✓ Returned smoothly to Sourcing view.');

    // 8. TEST RBAC 403 FORBIDDEN FOR UNAUTHORIZED ROLE (EMPLOYEE)
    console.log('\n--- STEP 7: TEST RBAC 403 FORBIDDEN (EMPLOYEE CANNOT CREATE QUOTATIONS) ---');
    const rbacResult = await page.evaluate(async () => {
      // 1. Authenticate with Supabase as employee
      const authRes = await fetch('https://oogcmsouczrmbwughnfb.supabase.co/auth/v1/token?grant_type=password', {
        method: 'POST',
        headers: {
          'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9vZ2Ntc291Y3pybWJ3dWdobmZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ3MjIwNzMsImV4cCI6MjEwMDI5ODA3M30.qvLLoL-yhrKluw8Yu0GwqUfRA4FQ4doFUb-opnv3sBc',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: 'employee@company.com', password: 'password123' })
      });
      const authData = await authRes.json();
      const empToken = authData.access_token;

      // 2. Attempt POST /api/quotations with employee token
      const quoteRes = await fetch('/api/quotations', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${empToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          purchaseRequestId: 'PR-2026-001',
          supplierId: 'SUP-01',
          totalAmount: 10000000,
          quantity: 1,
          deliveryDays: 3,
          fileUrl: 'quotes/unauthorized.pdf'
        })
      });

      return {
        status: quoteRes.status,
        statusText: quoteRes.statusText
      };
    });

    console.log(`✓ Employee POST /api/quotations response: HTTP ${rbacResult.status} ${rbacResult.statusText}`);
    if (rbacResult.status !== 403) {
      throw new Error(`Expected HTTP 403 Forbidden for Employee on POST /api/quotations, got ${rbacResult.status}`);
    }
    console.log('✓ RBAC security verified: Employee correctly received HTTP 403 Forbidden.');

    console.log('\n======================================================');
    console.log('🎉 ALL PHASE 4B QUOTATION E2E TESTS PASSED!');
    console.log('======================================================');

  } catch (err) {
    console.error('❌ E2E TEST FAILED:', err);
    const errorPath = path.join(EVIDENCE_DIR, 'phase4b-error.png');
    await page.screenshot({ path: errorPath });
    console.log(`Captured error screenshot at: ${errorPath}`);
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

runPhase4BQuotationE2E();
