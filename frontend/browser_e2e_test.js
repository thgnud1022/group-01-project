import puppeteer from 'puppeteer-core';
import fs from 'fs';

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

const TEST_USERS = [
  { email: 'employee@company.com', role: 'EMPLOYEE', expectedName: 'Nguyễn Văn A' },
  { email: 'manager@company.com', role: 'MANAGER', expectedName: 'Trần Văn B' },
  { email: 'procurement@company.com', role: 'PROCUREMENT', expectedName: 'Lê Thị C' },
  { email: 'finance@company.com', role: 'FINANCE', expectedName: 'Phạm Văn D' },
  { email: 'admin@company.com', role: 'ADMIN', expectedName: 'Quản Trị Viên' },
];

async function runBrowserTests() {
  console.log('=== STARTING BROWSER E2E TESTS ===');
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1181,796']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1181, height: 796 });

  const results = {
    accounts: [],
    sessionPersistence: false,
    logout: false,
    networkEvidence: null
  };

  // Listen to browser console
  page.on('console', msg => console.log(`[BROWSER] ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`[PAGE ERROR] ${err.message}`));

  // Monitor Network Requests
  let lastAuthHeader = null;
  page.on('request', request => {
    if (request.url().includes('/api/auth/me')) {
      const auth = request.headers()['authorization'];
      if (auth && auth.startsWith('Bearer ')) {
        lastAuthHeader = auth;
      }
    }
  });

  // Navigate once at the beginning
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2' });

  // 1. TEST ALL 5 ACCOUNTS
  for (const user of TEST_USERS) {
    console.log(`\n--- Testing Browser Login: ${user.email} (${user.role}) ---`);

    // Wait for login form
    await page.waitForSelector('[data-testid="input-email"]', { timeout: 10000 });
    await page.waitForSelector('[data-testid="input-password"]', { timeout: 10000 });

    // Fill form using Quick Account Button (verifying Section 10: pre-fill only)
    await page.evaluate((role) => {
      const btn = document.querySelector(`[data-testid="test-acc-${role}"]`);
      if (btn) btn.click();
    }, user.role.toLowerCase());

    await page.waitForFunction(
      (expectedEmail) => {
        const input = document.querySelector('[data-testid="input-email"]');
        return input && input.value === expectedEmail;
      },
      { timeout: 5000 },
      user.email
    );
    const filledEmail = await page.$eval('[data-testid="input-email"]', el => el.value);
    console.log(`Pre-filled email via button: ${filledEmail}`);

    // Submit
    lastAuthHeader = null;
    await page.waitForFunction(() => {
      const btn = document.querySelector('[data-testid="login-submit-button"]');
      return btn && !btn.disabled;
    });

    const [authMeRes] = await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/auth/me'), { timeout: 20000 }),
      page.evaluate(() => {
        const btn = document.querySelector('[data-testid="login-submit-button"]');
        if (btn) btn.click();
      })
    ]);

    if (authMeRes.status() !== 200) {
      const errText = await page.evaluate(() => {
        const el = document.querySelector('[data-testid="login-error-banner"]');
        return el ? el.innerText : 'Unknown error';
      });
      throw new Error(`Login failed for ${user.email}: Status ${authMeRes.status()} - ${errText}`);
    }

    // Verify AppShell loaded
    await page.waitForSelector('[data-testid="app-shell"]', { timeout: 10000 });
    
    // Check displayed user info
    const pageText = await page.evaluate(() => document.body.innerText);
    const hasName = pageText.includes(user.expectedName);
    const hasRole = pageText.includes(user.role);

    console.log(`AppShell verified: User=${user.expectedName} (Found: ${hasName}), Role=${user.role} (Found: ${hasRole})`);
    
    if (lastAuthHeader) {
      const token = lastAuthHeader.replace('Bearer ', '');
      const parts = token.split('.');
      let alg = 'UNKNOWN';
      try {
        const header = JSON.parse(Buffer.from(parts[0], 'base64').toString());
        alg = header.alg;
      } catch (e) {}

      results.networkEvidence = {
        bearerAttached: true,
        jwtAlgorithm: alg,
        tokenLength: token.length
      };
      console.log(`Network Evidence: Bearer attached: YES | Algorithm: ${alg}`);
    }

    results.accounts.push({
      email: user.email,
      role: user.role,
      name: user.expectedName,
      status: hasName && hasRole ? 'PASS' : 'FAIL'
    });

    // Logout if not the last one
    if (user.role !== 'ADMIN') {
      await page.waitForSelector('[data-testid="logout-button"]', { timeout: 5000 });
      await page.evaluate(() => {
        const btn = document.querySelector('[data-testid="logout-button"]');
        if (btn) btn.click();
      });
      await page.waitForSelector('[data-testid="input-email"]', { timeout: 10000 });
      console.log(`Logged out cleanly from ${user.email}`);
      await new Promise(r => setTimeout(r, 2000));
    }
  }

  // 2. TEST SESSION PERSISTENCE (using current ADMIN session)
  console.log('\n--- Testing Session Persistence across reload (ADMIN) ---');
  await page.reload({ waitUntil: 'networkidle2' });
  await page.waitForSelector('[data-testid="app-shell"]', { timeout: 10000 });
  const reloadedText = await page.evaluate(() => document.body.innerText);
  const stillLoggedIn = reloadedText.includes('Quản Trị Viên') && reloadedText.includes('ADMIN');
  console.log(`Session restored on reload: ${stillLoggedIn ? 'PASS' : 'FAIL'}`);
  results.sessionPersistence = stillLoggedIn;

  // 3. TEST LOGOUT & UNAUTHORIZED CHECK
  console.log('\n--- Testing Logout & Fail-Closed State ---');
  await page.waitForSelector('[data-testid="logout-button"]', { timeout: 5000 });
  await page.evaluate(() => {
    const btn = document.querySelector('[data-testid="logout-button"]');
    if (btn) btn.click();
  });
  await page.waitForSelector('[data-testid="input-email"]', { timeout: 10000 });
  const loginVisible = await page.$('[data-testid="input-email"]') !== null;
  console.log(`Returned to Login screen: ${loginVisible ? 'PASS' : 'FAIL'}`);
  results.logout = loginVisible;

  // Take screenshot of Login page
  await page.screenshot({ path: 'd:\\LTUD\\group-01-project-main\\docs\\evidence\\browser\\e2e-login-final.png' });

  // Login as EMPLOYEE again for AppShell screenshot
  await page.evaluate(() => {
    const btn = document.querySelector('[data-testid="test-acc-employee"]');
    if (btn) btn.click();
  });
  await page.waitForFunction(() => {
    const input = document.querySelector('[data-testid="input-email"]');
    return input && input.value === 'employee@company.com';
  });
  await Promise.all([
    page.waitForResponse(res => res.url().includes('/api/auth/me') && res.status() === 200, { timeout: 20000 }),
    page.evaluate(() => {
      const btn = document.querySelector('[data-testid="login-submit-button"]');
      if (btn) btn.click();
    })
  ]);
  await page.waitForSelector('[data-testid="app-shell"]', { timeout: 10000 });
  await page.screenshot({ path: 'd:\\LTUD\\group-01-project-main\\docs\\evidence\\browser\\e2e-appshell-final.png' });
  console.log('Screenshots saved: e2e-login-final.png, e2e-appshell-final.png');

  await browser.close();

  fs.writeFileSync(
    'd:\\LTUD\\group-01-project-main\\scratch\\browser_e2e_results.json',
    JSON.stringify(results, null, 2)
  );

  console.log('\n=== BROWSER E2E TESTS COMPLETED SUCCESSFULLY ===');
}

runBrowserTests().catch(err => {
  console.error('Browser Test Error:', err);
  process.exit(1);
});
