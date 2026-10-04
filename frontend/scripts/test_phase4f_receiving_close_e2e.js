import puppeteer from 'puppeteer-core';
import { execSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const EVIDENCE_DIR = path.resolve(__dirname, '../../docs/evidence/browser');

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function safeClick(page, selector) {
  await page.waitForSelector(selector, { visible: true, timeout: 15000 });
  await page.evaluate((sel) => {
    const el = document.querySelector(sel);
    if (!el) throw new Error(`Element ${sel} not found`);
    el.scrollIntoView({ behavior: 'instant', block: 'center' });
  }, selector);
  await delay(300);
  await page.click(selector);
}

async function dismissToast(page) {
  try {
    const toast = await page.$('.toast-notification, [data-testid="toast"]');
    if (toast) {
      await page.evaluate((el) => el.remove(), toast);
      await delay(200);
    }
  } catch (e) {
    // Ignore if no toast
  }
}

async function runPhase4FE2E() {
  console.log('=== STARTING PHASE 4F GOODS RECEIVING -> CLOSE PR BROWSER E2E ===\n');

  const pythonExe = path.resolve(__dirname, '../../backend/.venv/Scripts/python.exe');

  // 1. Ensure test users are ready (skip sync if not needed)
  console.log('1. Preparing test environment...');

  // 2. Seed fresh PO for Phase 4F testing
  console.log('2. Seeding fresh PO (quantity: 5, status: SENT) in PostgreSQL...');
  const seedScript = path.resolve(__dirname, '../../backend/scratch/seed_phase4f_data.py');
  const seedOutput = execSync(`"${pythonExe}" "${seedScript}"`, {
    cwd: path.resolve(__dirname, '../../backend')
  }).toString();

  const lines = seedOutput.trim().split('\n');
  const jsonLine = lines.find(l => l.trim().startsWith('{'));
  if (!jsonLine) {
    throw new Error('Failed to parse seed output JSON: ' + seedOutput);
  }
  const seedData = JSON.parse(jsonLine.trim());
  console.log(`✓ Seeded PR: ${seedData.prId}`);
  console.log(`✓ Seeded PO: ${seedData.poNumber} (ID: ${seedData.poId})`);
  console.log(`  - Ordered Quantity: ${seedData.quantity} units`);
  console.log(`  - Total Amount: ${seedData.totalAmount.toLocaleString()} ₫`);
  console.log(`  - Supplier: ${seedData.supplierName}`);

  // 3. Launch Puppeteer browser
  console.log('\n3. Launching browser...');
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    defaultViewport: { width: 1440, height: 1080 },
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  page.on('console', msg => {
    const text = msg.text();
    if (text.includes('[BROWSER]') || text.includes('error') || text.includes('Error')) {
      console.log(`[BROWSER] ${msg.type()}: ${text}`);
    }
  });

  try {
    console.log('Navigating to http://localhost:5173/...');
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2', timeout: 30000 });

    // 4. Authenticate as admin@company.com (has PROCUREMENT write and ADMIN close authority)
    console.log('Authenticating as admin@company.com...');
    await page.waitForSelector('[data-testid="input-email"]', { timeout: 15000 });
    
    // Use test-acc-admin quick button if present, or type
    const adminBtn = await page.$('[data-testid="test-acc-admin"]');
    if (adminBtn) {
      await adminBtn.click();
      await delay(300);
    } else {
      await page.type('[data-testid="input-email"]', 'admin@company.com');
      await page.type('[data-testid="input-password"]', 'admin123');
    }

    await page.waitForSelector('[data-testid="login-submit-button"]', { timeout: 5000 });
    const [authMeRes] = await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/auth/me') || res.url().includes('/api/auth/login'), { timeout: 20000 }),
      page.click('[data-testid="login-submit-button"]')
    ]);
    console.log(`Auth response status: ${authMeRes.status()}`);

    await page.waitForSelector('[data-testid="app-shell"]', { timeout: 15000 });
    console.log('✓ AppShell loaded.');

    // 5. Navigate to Purchase Orders Tab (Figma 9:6424)
    console.log('\n--- STEP 1: NAVIGATE TO PURCHASE ORDERS VIEW (FIGMA 9:6424) ---');
    await safeClick(page, '[data-testid="nav-purchase-orders"]');
    await page.waitForSelector('[data-testid="purchase-orders-view"]', { timeout: 15000 });
    await delay(600);
    await dismissToast(page);

    // 6. Locate our seeded PO under "Issued — awaiting delivery"
    console.log(`\n--- STEP 2: OPEN PO DETAIL FOR ${seedData.poNumber} ---`);
    const poCardSelector = `[data-testid="po-card-${seedData.poId}"]`;
    await page.waitForSelector(poCardSelector, { timeout: 15000 });
    await safeClick(page, poCardSelector);

    // 7. Verify PO Detail / Receive Goods view loaded (Figma 9:6580)
    await page.waitForSelector('[data-testid="po-detail-view"]', { timeout: 15000 });
    await page.waitForSelector('[data-testid="record-goods-section"]', { timeout: 15000 });
    console.log('✓ PO Detail / Receiving View (Figma 9:6580) loaded.');

    // 8. PARTIAL RECEIPT: Receive 2 of 5 units
    console.log('\n--- STEP 3: RECORD PARTIAL RECEIPT (2 / 5 UNITS) ---');
    await safeClick(page, '[data-testid="condition-part-radio"]');
    await delay(300);

    await page.waitForSelector('[data-testid="received-qty-input"]', { timeout: 5000 });
    await page.$eval('[data-testid="received-qty-input"]', el => el.value = '');
    await page.type('[data-testid="received-qty-input"]', '2');

    await page.$eval('[data-testid="receipt-note-input"]', el => el.value = '');
    await page.type('[data-testid="receipt-note-input"]', 'Đợt 1 nhận trước 2 màn hình kiểm định chất lượng');

    const [rec1Response] = await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/receiving') && res.request().method() === 'POST', { timeout: 15000 }),
      safeClick(page, '[data-testid="submit-receipt-btn"]')
    ]);

    if (rec1Response.status() !== 200) {
      const errText = await rec1Response.text();
      throw new Error(`Partial receive failed: ${errText}`);
    }
    const rec1Data = await rec1Response.json();
    console.log(`✓ Partial receiving recorded in PostgreSQL:`);
    console.log(`  - Received: ${rec1Data.receivedQty} units`);
    console.log(`  - Total Received: ${rec1Data.totalReceived} / ${rec1Data.poQuantity} units`);

    await delay(600);
    // Capture partial receiving screenshot
    const receivingScreenshot = path.join(EVIDENCE_DIR, 'po-receiving-browser.png');
    await page.screenshot({ path: receivingScreenshot, fullPage: true });
    console.log('✓ Captured Figma 9:6580 partial receiving screenshot:', receivingScreenshot);

    // 9. REMAINING RECEIPT: Receive remaining 3 of 5 units (completion)
    console.log('\n--- STEP 4: RECORD REMAINING RECEIPT (3 / 3 UNITS -> 5 / 5 TOTAL) ---');
    await safeClick(page, '[data-testid="condition-full-radio"]');
    await delay(300);

    await page.$eval('[data-testid="receipt-note-input"]', el => el.value = '');
    await page.type('[data-testid="receipt-note-input"]', 'Đợt 2 nhận đủ 3 màn hình còn lại. Bàn giao đầy đủ CO/CQ.');

    const [rec2Response] = await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/receiving') && res.request().method() === 'POST', { timeout: 15000 }),
      safeClick(page, '[data-testid="submit-receipt-btn"]')
    ]);

    if (rec2Response.status() !== 200) {
      const errText = await rec2Response.text();
      throw new Error(`Remaining receive failed: ${errText}`);
    }
    const rec2Data = await rec2Response.json();
    console.log(`✓ Full receiving achieved in PostgreSQL:`);
    console.log(`  - Received: ${rec2Data.receivedQty} units`);
    console.log(`  - Cumulative Total: ${rec2Data.totalReceived} / ${rec2Data.poQuantity} units`);

    // Verify UI shows Received in Full notice and Close PR section
    await page.waitForSelector('[data-testid="received-in-full-card"]', { timeout: 15000 });
    await page.waitForSelector('[data-testid="close-po-section"]', { timeout: 15000 });
    console.log('✓ UI transitioned to Received in full state.');

    // 10. CLOSE PURCHASE ORDER (HD-07)
    console.log('\n--- STEP 5: CLOSE PURCHASE ORDER (HD-07 / BUDGET SETTLEMENT) ---');
    const [closeResponse] = await Promise.all([
      page.waitForResponse(res => res.url().includes('/close') && res.request().method() === 'POST', { timeout: 15000 }),
      safeClick(page, '[data-testid="close-po-btn"]')
    ]);

    if (closeResponse.status() !== 200) {
      const errText = await closeResponse.text();
      throw new Error(`Close PR failed: ${errText}`);
    }
    const closeData = await closeResponse.json();
    console.log(`✓ PR closed successfully via PostgreSQL:`);
    console.log(`  - PR ID: ${closeData.id}`);
    console.log(`  - Status: ${closeData.status}`);
    console.log(`  - Settled Amount: ${closeData.settledAmount.toLocaleString()} ₫`);

    // Verify UI transitions to Figma 9:6793 (Order Closed)
    await page.waitForSelector('[data-testid="order-closed-card"]', { timeout: 15000 });
    await page.waitForSelector('[data-testid="po-detail-closed-badge"]', { timeout: 10000 });
    console.log('✓ UI transitioned to PO Closed state (Figma 9:6793).');

    // Capture closed PO screenshot
    const closedPoScreenshot = path.join(EVIDENCE_DIR, 'po-closed-browser.png');
    await page.screenshot({ path: closedPoScreenshot, fullPage: true });
    console.log('✓ Captured Figma 9:6793 PO Closed screenshot:', closedPoScreenshot);

    // 11. Navigate back to Purchase Orders List (Figma 9:6424)
    console.log('\n--- STEP 6: BACK TO PURCHASE ORDERS LIST (FIGMA 9:6424 CLOSED STATE) ---');
    await safeClick(page, '[data-testid="back-to-pos-btn"]');
    await page.waitForSelector('[data-testid="purchase-orders-view"]', { timeout: 15000 });
    await delay(600);

    // Verify PO now resides under "Closed" section
    const closedPoCardSelector = `[data-testid="closed-po-card-${seedData.poId}"]`;
    await page.waitForSelector(closedPoCardSelector, { timeout: 15000 });
    console.log(`✓ PO ${seedData.poNumber} verified in 'Closed' section.`);

    // Capture Figma 9:6424 closed list screenshot
    const closedListScreenshot = path.join(EVIDENCE_DIR, 'purchase-orders-closed-browser.png');
    await page.screenshot({ path: closedListScreenshot, fullPage: true });
    console.log('✓ Captured Figma 9:6424 Closed List screenshot:', closedListScreenshot);

    // 12. Run Database Authority & Integrity Verification script
    console.log('\n--- STEP 7: DATABASE AUTHORITY & INTEGRITY VERIFICATION ---');
    const integrityScript = path.resolve(__dirname, '../../backend/scratch/verify_phase4f_db_integrity.py');
    const integrityOutput = execSync(`"${pythonExe}" "${integrityScript}" "${seedData.prId}" "${seedData.poId}"`, {
      cwd: path.resolve(__dirname, '../../backend')
    }).toString();
    console.log(integrityOutput.trim());

    console.log('\n=== ALL PHASE 4F BROWSER E2E TESTS PASSED SUCCESSFULLY! ===');
  } finally {
    await browser.close();
  }
}

runPhase4FE2E().catch(err => {
  console.error('\n❌ BROWSER E2E FAILED:', err);
  process.exit(1);
});
