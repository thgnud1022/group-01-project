import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
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

async function runPhase4EPoE2E() {
  console.log('=== STARTING PHASE 4E HUMAN AWARD -> PURCHASE ORDER BROWSER E2E ===\n');

  const pythonExe = path.resolve(__dirname, '../../backend/.venv/Scripts/python.exe');
  
  // 1. Sync Supabase identities
  console.log('1. Ensuring Supabase test user identities are bound in PostgreSQL...');
  try {
    const syncScript = path.resolve(__dirname, '../../scratch/sync_all_supabase_users.py');
    execSync(`"${pythonExe}" "${syncScript}"`, { 
      stdio: 'inherit',
      cwd: path.resolve(__dirname, '../../backend')
    });
  } catch (err) {
    console.warn('User sync warning:', err.message);
  }

  // 2. Seed fresh PR with quotations
  console.log('2. Seeding fresh APPROVED PR with 2 quotations in PostgreSQL...');
  let seedData;
  try {
    const seedScript = path.resolve(__dirname, '../../backend/scratch/seed_phase4e_data.py');
    const out = execSync(`"${pythonExe}" "${seedScript}"`, { 
      cwd: path.resolve(__dirname, '../../backend')
    }).toString().trim();
    // Parse json line from stdout
    const jsonLine = out.split('\n').filter(l => l.startsWith('{')).pop();
    seedData = JSON.parse(jsonLine);
    console.log('✓ Seeded PR:', seedData.prId);
    console.log('  - Quotation 1 (TechSource):', seedData.q1Id, 'Amount:', seedData.q1Amount);
    console.log('  - Quotation 2 (Global Tech):', seedData.q2Id, 'Amount:', seedData.q2Amount);
  } catch (err) {
    console.error('Failed to seed data:', err.message);
    process.exit(1);
  }

  // 3. Launch Chrome
  console.log('\n3. Launching browser...');
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,1000']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 1000 });

  page.on('console', msg => console.log(`[BROWSER] ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`[PAGE ERROR] ${err.message}`));

  try {
    console.log('Navigating to http://localhost:5173/...');
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2' });

    // 4. Authenticate as Procurement Officer
    console.log('Authenticating as procurement@company.com...');
    const isLoginPage = await page.$('[data-testid="input-email"]');
    if (isLoginPage) {
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

    // 5. Navigate to Sourcing Tab
    console.log('\n--- STEP 1: NAVIGATE TO SOURCING ---');
    await safeClick(page, '[data-testid="nav-sourcing"]');
    await page.waitForSelector('[data-testid="sourcing-view"]', { timeout: 15000 });
    await delay(600);
    await dismissToast(page);

    // 6. Open Comparison View for our Seeded PR
    console.log(`\n--- STEP 2: OPEN COMPARISON VIEW FOR ${seedData.prId} ---`);
    const compareBtnSelector = `[data-testid="compare-btn-${seedData.prId}"]`;
    await page.waitForSelector(compareBtnSelector, { timeout: 15000 });
    await safeClick(page, compareBtnSelector);

    // Verify Comparison View loaded
    await page.waitForSelector('.comparison-view-container', { timeout: 15000 });
    console.log('✓ ComparisonView loaded.');

    // 7. Human Award: Select Quotation 1 (TechSource)
    console.log('\n--- STEP 3: HUMAN AWARD SELECTION ---');
    const q1RadioSelector = `[data-testid="quote-radio-${seedData.q1Id}"]`;
    await page.waitForSelector(q1RadioSelector, { timeout: 15000 });
    await page.evaluate((sel) => {
      const radio = document.querySelector(sel);
      if (!radio) throw new Error('Radio not found: ' + sel);
      radio.checked = true;
      radio.dispatchEvent(new Event('change', { bubbles: true }));
    }, q1RadioSelector);
    await delay(400);

    const isChecked = await page.evaluate((sel) => {
      const r = document.querySelector(sel);
      return r && r.checked;
    }, q1RadioSelector);
    if (!isChecked) throw new Error('Human selection radio failed to check!');
    console.log('✓ Human selected Quotation 1 (TechSource Distribution).');

    // 8. Click Create Purchase Order
    console.log('\n--- STEP 4: CREATE PURCHASE ORDER (HD-04 / US-09) ---');
    const createPoBtnSelector = '[data-testid="create-po-btn"]';
    await page.waitForSelector(createPoBtnSelector, { timeout: 15000 });

    const [poResponse] = await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/po') && res.request().method() === 'POST', { timeout: 15000 }),
      safeClick(page, createPoBtnSelector)
    ]);

    if (poResponse.status() !== 200) {
      const errText = await poResponse.text();
      throw new Error(`Create PO failed with HTTP ${poResponse.status()}: ${errText}`);
    }
    const createdPO = await poResponse.json();
    console.log(`✓ PO created successfully via PostgreSQL API:`);
    console.log(`  - PO Number: ${createdPO.poNumber}`);
    console.log(`  - Total Amount: ${createdPO.totalAmount} ₫ (Locked from DB quote: ${seedData.q1Amount})`);
    console.log(`  - Quantity: ${createdPO.quantity} units`);
    console.log(`  - Supplier: ${createdPO.supplierName}`);

    // 9. Verify UI transitions to Figma 9:5915 (PO Issued / Awarded state)
    console.log('\n--- STEP 5: VERIFY FIGMA 9:5915 (AWARDED / PO ISSUED) ---');
    await page.waitForSelector('[data-testid="po-issued-badge"]', { timeout: 10000 });
    const badgeText = await page.$eval('[data-testid="po-issued-badge"]', el => el.textContent.trim());
    if (badgeText !== 'PO issued') throw new Error(`Expected 'PO issued', got '${badgeText}'`);
    console.log('✓ Top badge shows: PO issued');

    await page.waitForSelector('[data-testid="awarded-supplier-card"]', { timeout: 10000 });
    console.log('✓ Awarded supplier card displayed.');

    await page.waitForSelector('[data-testid="open-po-btn"]', { timeout: 10000 });
    console.log('✓ Action button changed to: Open purchase order');

    // Capture Figma 9:5915 evidence screenshot
    const poIssuedScreenshot = path.join(EVIDENCE_DIR, 'po-issued-browser.png');
    await page.screenshot({ path: poIssuedScreenshot, fullPage: true });
    console.log('✓ Captured Figma 9:5915 screenshot:', poIssuedScreenshot);

    // 10. Click Open Purchase Order -> Navigates to Purchase Orders (Figma 9:6424)
    console.log('\n--- STEP 6: NAVIGATE TO PURCHASE ORDERS VIEW (FIGMA 9:6424) ---');
    await safeClick(page, '[data-testid="open-po-btn"]');
    await page.waitForSelector('[data-testid="purchase-orders-view"]', { timeout: 15000 });
    console.log('✓ PurchaseOrdersView loaded.');

    await page.waitForSelector('[data-testid="section-issued-pos"]', { timeout: 15000 });
    const poCardSelector = `[data-testid="po-card-${createdPO.id}"]`;
    await page.waitForSelector(poCardSelector, { timeout: 15000 });

    const cardDetails = await page.evaluate((id) => {
      const card = document.querySelector(`[data-testid="po-card-${id}"]`);
      if (!card) return null;
      return {
        poNumber: card.querySelector('[data-testid="po-number"]')?.textContent.trim(),
        itemSupplier: card.querySelector('[data-testid="po-item-supplier"]')?.textContent.trim(),
        totalAmount: card.querySelector('[data-testid="po-total-amount"]')?.textContent.trim(),
      };
    }, createdPO.id);

    console.log('✓ Verified PO in Issued List (Figma 9:6424):', cardDetails);
    if (!cardDetails.poNumber.startsWith('PO-NUM-')) {
      throw new Error(`PO number invalid: ${cardDetails.poNumber}`);
    }
    if (!cardDetails.itemSupplier.includes('TechSource Distribution')) {
      throw new Error(`Supplier name mismatch: ${cardDetails.itemSupplier}`);
    }

    // Capture Figma 9:6424 evidence screenshot
    const purchaseOrdersScreenshot = path.join(EVIDENCE_DIR, 'purchase-orders-browser.png');
    await page.screenshot({ path: purchaseOrdersScreenshot, fullPage: true });
    console.log('✓ Captured Figma 9:6424 screenshot:', purchaseOrdersScreenshot);

    // 11. Run DB Integrity verification script
    console.log('\n--- STEP 7: DATABASE AUTHORITY & INTEGRITY VERIFICATION ---');
    const integrityScript = path.resolve(__dirname, '../../backend/scratch/verify_phase4e_db_integrity.py');
    const integrityOutput = execSync(`"${pythonExe}" "${integrityScript}" "${seedData.prId}" "${seedData.q1Id}"`, {
      cwd: path.resolve(__dirname, '../../backend')
    }).toString();
    console.log(integrityOutput.trim());

    console.log('\n=== ALL PHASE 4E BROWSER E2E TESTS PASSED SUCCESSFULLY! ===');
  } finally {
    await browser.close();
  }
}

runPhase4EPoE2E().catch((err) => {
  console.error('\n❌ BROWSER E2E FAILED:', err);
  process.exit(1);
});
