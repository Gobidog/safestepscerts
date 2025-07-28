const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Navigate to app
    await page.goto('http://localhost:8503');
    await page.waitForTimeout(2000);
    
    // Fill in admin credentials
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'Admin@SafeSteps2024');
    
    // Click login button
    await page.click('button:has-text("Login")');
    await page.waitForTimeout(3000);
    
    // Check if login was successful
    const pageContent = await page.content();
    if (pageContent.includes('Admin Dashboard') || pageContent.includes('Certificate Generator')) {
      console.log('✅ Admin login successful\!');
    } else {
      console.log('❌ Admin login failed');
    }
    
    // Take screenshot
    await page.screenshot({ path: 'admin_login_test.png' });
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
})();
