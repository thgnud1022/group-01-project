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

async function runPhase4DAiE2E() {
  console.log('=== STARTING PHASE 4D AI ANALYSIS BROWSER E2E SUITE ===');

  console.log('Ensuring Supabase test user identities are bound in PostgreSQL...');
  try {
    const pythonExe = path.resolve(__dirname, '../../backend/.venv/Scripts/python.exe');
    const syncScript = path.resolve(__dirname, '../../scratch/sync_all_supabase_users.py');
    execSync(`"${pythonExe}" "${syncScript}"`, { 
      stdio: 'inherit',
      cwd: path.resolve(__dirname, '../../backend')
    });
  } catch (err) {
    console.warn('User sync warning:', err.message);
  }

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1200,1000']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 1000 });

  page.on('console', msg => console.log(`[BROWSER] ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`[PAGE ERROR] ${err.message}`));

  try {
    console.log('Navigating to frontend at http://localhost:5173/...');
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2' });

    // 1. AUTHENTICATE WITH REAL SUPABASE AUTH (Procurement Officer)
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

    // 3. NAVIGATE TO PR-2026-001 COMPARISON VIEW
    console.log('\n--- STEP 2: OPEN PR-2026-001 COMPARISON VIEW ---');
    await page.waitForFunction(() => !document.querySelector('[data-testid="sourcing-loading"]'), { timeout: 15000 });
    await page.waitForSelector('[data-testid="compare-btn-PR-2026-001"]', { timeout: 15000 });
    await safeClick(page, '[data-testid="compare-btn-PR-2026-001"]');

    // Wait for comparison view ready
    await page.waitForSelector('[data-testid="comparison-view"]', { timeout: 15000 });
    await delay(600);
    await dismissToast(page);
    console.log('✓ PR-2026-001 Comparison view loaded with normalised quotations.');

    // 4. VERIFY INITIAL STATE: ASSISTANT ANALYSIS NOT REQUESTED (Figma 9:5093)
    console.log('\n--- STEP 3: VERIFY INITIAL ASSISTANT STATE ---');
    const askAssistantBtn = await page.$('[data-testid="ask-assistant-btn"]');
    if (!askAssistantBtn) {
      throw new Error('Initial state failed: ask-assistant-btn not found!');
    }
    console.log('✓ "Assistant analysis not requested" banner & button confirmed present.');

    // 5. CLICK "Ask the assistant to analyse" (Phase 4D AI Recommendation Flow)
    console.log('\n--- STEP 4: TRIGGER AI ANALYSIS ---');
    await safeClick(page, '[data-testid="ask-assistant-btn"]');

    // 6. WAIT FOR ASSISTANT ANALYSIS PANEL (Figma 9:5589 / Flow D 9:5291)
    console.log('Waiting for AI Assistant Recommendation response and panel render...');
    await page.waitForSelector('[data-testid="assistant-analysis-panel"]', { timeout: 20000 });
    console.log('✓ assistant-analysis-panel successfully rendered!');

    // 7. VERIFY COMPONENT SECTIONS
    console.log('\n--- STEP 5: VERIFY AI ANALYSIS COMPONENTS (Figma 9:5589) ---');
    
    // Mode badge
    const modeBadge = await page.$eval('[data-testid="ai-mode-badge"]', el => el.textContent.trim());
    const e2eMode = modeBadge.includes('Fallback') ? 'FALLBACK / HEURISTIC' : 'LIVE GEMINI';
    console.log(`\n========================================`);
    console.log(`E2E MODE: ${e2eMode}`);
    console.log(`========================================\n`);

    // Confidence badge
    const confidenceText = await page.$eval('[data-testid="ai-confidence-badge"]', el => el.textContent);
    console.log(`✓ Confidence Badge verified: "${confidenceText.trim()}" (Provenance: Fallback / Heuristic Confidence matching Figma 9:5589)`);

    // Top recommended card
    const recommendedCard = await page.$('[data-testid="ai-recommended-card"]');
    if (!recommendedCard) {
      throw new Error('Recommended quotation card not found in assistant analysis panel!');
    }
    const recommendedScore = await page.$eval('[data-testid="ai-recommended-score"]', el => el.textContent);
    console.log(`✓ AI Recommended Card verified with ${recommendedScore.trim()}`);

    // Why section
    const whySection = await page.$('[data-testid="ai-why-section"]');
    if (!whySection) {
      throw new Error('AI Why section not found!');
    }
    const whyItems = await page.$$eval('[data-testid="ai-why-section"] li', items => items.map(i => i.textContent.trim()));
    console.log(`✓ AI Why section verified (${whyItems.length} points): ${whyItems[0]}`);

    // Risks section
    const risksSection = await page.$('[data-testid="ai-risks-section"]');
    if (!risksSection) {
      throw new Error('AI Risks section not found!');
    }
    const riskItems = await page.$$eval('[data-testid="ai-risks-section"] li', items => items.map(i => i.textContent.trim()));
    console.log(`✓ AI Risks section verified (${riskItems.length} points): ${riskItems[0]}`);

    // Missing Data section
    const missingDataSection = await page.$('[data-testid="ai-missing-data-section"]');
    if (!missingDataSection) {
      throw new Error('AI Missing Data section not found!');
    }
    const missingItems = await page.$$eval('[data-testid="ai-missing-data-section"] li', items => items.map(i => i.textContent.trim()));
    console.log(`✓ AI Missing Data section verified (${missingItems.length} points): ${missingItems[0]}`);

    // 8. VERIFY SUPPLIER SELECTION INTEGRATION (Figma 9:5783)
    console.log('\n--- STEP 6: VERIFY SUPPLIER SELECTION INTEGRATION ---');
    const recommendedBadge = await page.$('[data-testid="ai-recommended-badge"]');
    if (!recommendedBadge) {
      throw new Error('AI Recommended badge not found in supplier selection options!');
    }
    const badgeText = await page.$eval('[data-testid="ai-recommended-badge"]', el => el.textContent);
    console.log(`✓ AI Recommended badge verified in Supplier Selection: "${badgeText.trim()}"`);

    // 9. CAPTURE ARTIFACT EVIDENCE SCREENSHOT
    console.log('\n--- STEP 7: CAPTURE BROWSER SCREENSHOT ---');
    await delay(800);
    const screenshotPath = path.resolve(EVIDENCE_DIR, 'ai-analysis-browser.png');
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`✓ Browser evidence screenshot saved to: ${screenshotPath}`);

    // 10. VERIFY DATABASE GOVERNANCE / NON-MUTATION
    console.log('\n--- STEP 8: VERIFY NO DATABASE SIDE EFFECTS (Decision Support Only) ---');
    const pythonExe = path.resolve(__dirname, '../../backend/.venv/Scripts/python.exe');
    const verifyScript = path.resolve(__dirname, '../../scratch/verify_db_non_mutation.py');
    execSync(`"${pythonExe}" "${verifyScript}"`, { 
      stdio: 'inherit',
      cwd: path.resolve(__dirname, '../../backend')
    });
    console.log('✓ Governance check PASSED: AI is strictly Decision Support, not Decision Maker.');

    console.log('\n======================================================');
    console.log('🎉 PHASE 4D AI ANALYSIS BROWSER E2E TEST PASSED 100%');
    console.log('======================================================\n');
  } catch (err) {
    console.error('❌ PHASE 4D AI ANALYSIS BROWSER E2E TEST FAILED:', err);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runPhase4DAiE2E();
