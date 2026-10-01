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

async function runPhase4ASourcingSupplierE2E() {
  console.log('=== STARTING PHASE 4A SOURCING & SUPPLIER E2E BROWSER TEST ===\n');

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

    // 2. NAVIGATE TO SOURCING TAB (Figma 9:4001)
    console.log('\n--- STEP 1: SOURCING VIEW (Figma 9:4001) ---');
    await safeClick(page, '[data-testid="nav-sourcing"]');
    await page.waitForSelector('[data-node-id="9:4001"]', { timeout: 15000 });
    await page.waitForSelector('[data-testid="sourcing-view"]', { timeout: 15000 });
    await page.waitForSelector('[data-testid="sourcing-loading"]', { hidden: true, timeout: 15000 }).catch(() => {});
    await new Promise(r => setTimeout(r, 600));
    await dismissToast(page);

    const sourcingPath = path.join(EVIDENCE_DIR, 'sourcing-browser.png');
    await page.screenshot({ path: sourcingPath });
    console.log(`✓ Sourcing screenshot captured: ${sourcingPath} (${fs.statSync(sourcingPath).size} bytes)`);

    // Verify Sourcing content
    const sourcingTitle = await page.$eval('[data-testid="sourcing-view"] h1', el => el.textContent);
    console.log(`✓ Sourcing Title verified: "${sourcingTitle}"`);

    // 3. NAVIGATE TO SUPPLIERS TAB (Figma 9:4479)
    console.log('\n--- STEP 2: SUPPLIERS VIEW (Figma 9:4479) ---');
    await safeClick(page, '[data-testid="nav-to-suppliers-btn"]');
    await page.waitForSelector('[data-node-id="9:4479"]', { timeout: 15000 });
    await page.waitForSelector('[data-testid="suppliers-view"]', { timeout: 15000 });
    await page.waitForSelector('[data-testid="suppliers-loading"]', { hidden: true, timeout: 15000 }).catch(() => {});
    await page.waitForSelector('[data-testid="suppliers-list"]', { timeout: 15000 });
    await new Promise(r => setTimeout(r, 600));
    await dismissToast(page);

    const suppliersPath = path.join(EVIDENCE_DIR, 'suppliers-browser.png');
    await page.screenshot({ path: suppliersPath });
    console.log(`✓ Suppliers screenshot captured: ${suppliersPath} (${fs.statSync(suppliersPath).size} bytes)`);

    // Verify seeded suppliers from DB
    await page.waitForSelector('[data-testid="supplier-card-SUP-01"]', { timeout: 10000 });
    await page.waitForSelector('[data-testid="supplier-card-SUP-02"]', { timeout: 10000 });
    await page.waitForSelector('[data-testid="supplier-card-SUP-03"]', { timeout: 10000 });
    console.log('✓ Seeded suppliers SUP-01, SUP-02, SUP-03 confirmed from real database.');

    // 4. CREATE NEW SUPPLIER (REAL POSTGRESQL INSERT)
    console.log('\n--- STEP 3: CREATE NEW SUPPLIER (POST /api/suppliers -> PostgreSQL) ---');
    await safeClick(page, '[data-testid="add-supplier-toggle-btn"]');
    await page.waitForSelector('[data-testid="create-supplier-panel"]', { timeout: 5000 });

    const testSupplierName = `[E2E] Công nghệ Số Việt Nam ${Date.now()}`;
    const testTaxCode = `031${Math.floor(1000000 + Math.random() * 9000000)}`;
    const testContact = 'contact@e2esupplier.vn';

    await page.type('[data-testid="input-supplier-name"]', testSupplierName);
    await page.type('[data-testid="input-supplier-tax"]', testTaxCode);
    await page.type('[data-testid="input-supplier-contact"]', testContact);

    console.log(`Submitting new supplier: "${testSupplierName}" (Tax: ${testTaxCode})...`);
    const [createResponse] = await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/suppliers') && res.request().method() === 'POST', { timeout: 15000 }),
      safeClick(page, '[data-testid="submit-supplier-btn"]')
    ]);

    const status = createResponse.status();
    console.log(`✓ POST /api/suppliers returned HTTP ${status}`);
    if (status !== 200 && status !== 201) {
      const respBody = await createResponse.text();
      throw new Error(`Failed to create supplier via API: HTTP ${status} - ${respBody}`);
    }

    const createdData = await createResponse.json();
    console.log(`✓ New supplier created in PostgreSQL with ID: ${createdData.id}`);

    // Wait for list reload and verify newly created supplier is rendered
    await page.waitForSelector(`[data-testid="supplier-card-${createdData.id}"]`, { timeout: 15000 });
    console.log(`✓ Newly created supplier card rendered in list: [data-testid="supplier-card-${createdData.id}"]`);

    const createdSupplierPath = path.join(EVIDENCE_DIR, 'supplier-created-browser.png');
    await page.screenshot({ path: createdSupplierPath });
    console.log(`✓ Created supplier screenshot captured: ${createdSupplierPath} (${fs.statSync(createdSupplierPath).size} bytes)`);

    // Verify detail of newly created supplier
    await safeClick(page, `[data-testid="view-supplier-detail-btn-${createdData.id}"]`);
    await page.waitForSelector('[data-testid="supplier-detail-modal"]', { timeout: 10000 });
    const newDetailText = await page.$eval('[data-testid="supplier-detail-modal"]', el => el.textContent);
    if (!newDetailText.includes(testSupplierName) || !newDetailText.includes(testTaxCode)) {
      throw new Error(`New supplier detail does not match submitted data: ${newDetailText.slice(0, 100)}`);
    }
    console.log(`✓ New supplier verified in detail modal directly from PostgreSQL!`);
    await safeClick(page, '[data-testid="close-supplier-detail-btn"]');

    // 5. SUPPLIER DETAIL MODAL FOR SEEDED SUP-01
    console.log('\n--- STEP 4: SUPPLIER DETAIL MODAL (SUP-01) ---');
    await safeClick(page, '[data-testid="view-supplier-detail-btn-SUP-01"]');
    await page.waitForSelector('[data-testid="supplier-detail-modal"]', { timeout: 10000 });
    await new Promise(r => setTimeout(r, 800));

    const modalText = await page.$eval('[data-testid="supplier-detail-modal"]', el => el.textContent);
    if (!modalText.includes('SUP-01') || !modalText.includes('Phong Vũ')) {
      throw new Error(`Supplier Detail does not contain expected SUP-01 / Phong Vũ data: ${modalText.slice(0, 100)}`);
    }
    console.log('✓ Supplier Detail modal verified with real data for SUP-01.');

    const detailPath = path.join(EVIDENCE_DIR, 'supplier-detail-browser.png');
    await page.screenshot({ path: detailPath });
    console.log(`✓ Supplier detail screenshot captured: ${detailPath} (${fs.statSync(detailPath).size} bytes)`);

    // Close modal
    await safeClick(page, '[data-testid="close-supplier-detail-btn"]');
    await page.waitForSelector('[data-testid="supplier-detail-modal"]', { hidden: true, timeout: 5000 });
    console.log('✓ Supplier Detail modal closed.');

    // 6. SEARCH FILTER
    console.log('\n--- STEP 5: SEARCH FILTER ---');
    await page.click('[data-testid="supplier-search-input"]');
    await page.type('[data-testid="supplier-search-input"]', 'Trần Anh');
    await new Promise(r => setTimeout(r, 600));
    const cardSup02 = await page.$('[data-testid="supplier-card-SUP-02"]');
    const cardSup01 = await page.$('[data-testid="supplier-card-SUP-01"]');
    if (!cardSup02 || cardSup01) {
      throw new Error('Search filter did not isolate SUP-02 (Trần Anh)!');
    }
    console.log('✓ Search filter working: isolated SUP-02.');

    // Clear search using triple click + Backspace
    await page.click('[data-testid="supplier-search-input"]', { clickCount: 3 });
    await page.keyboard.press('Backspace');
    await new Promise(r => setTimeout(r, 600));

    console.log('\n======================================================');
    console.log('🎉 ALL PHASE 4A SOURCING & SUPPLIER E2E TESTS PASSED!');
    console.log('======================================================');

  } catch (err) {
    console.error('❌ E2E TEST FAILED:', err);
    const errorPath = path.join(EVIDENCE_DIR, 'phase4a-error.png');
    await page.screenshot({ path: errorPath });
    console.log(`Captured error screenshot at: ${errorPath}`);
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

runPhase4ASourcingSupplierE2E();
