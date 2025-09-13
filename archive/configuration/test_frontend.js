const puppeteer = require('puppeteer');

async function testFrontend() {
  let browser;
  try {
    console.log('🚀 启动浏览器测试...');
    
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // 监听控制台错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log('❌ 控制台错误:', msg.text());
      }
    });
    
    // 监听页面错误
    page.on('pageerror', error => {
      console.log('❌ 页面错误:', error.message);
    });
    
    console.log('📱 访问前端页面...');
    await page.goto('http://localhost:3000', { 
      waitUntil: 'networkidle0',
      timeout: 30000 
    });
    
    // 等待页面加载
    await page.waitForTimeout(3000);
    
    // 检查页面标题
    const title = await page.title();
    console.log('📄 页面标题:', title);
    
    // 检查是否有React错误边界
    const errorBoundary = await page.$('.error-boundary');
    if (errorBoundary) {
      const errorText = await page.evaluate(el => el.textContent, errorBoundary);
      console.log('❌ 发现错误边界:', errorText);
      return false;
    }
    
    // 检查是否有登录表单或仪表板
    const loginForm = await page.$('form');
    const dashboard = await page.$('.dashboard-page');
    
    if (loginForm) {
      console.log('✅ 检测到登录页面');
      
      // 尝试登录
      await page.type('input[name="username"]', 'admin');
      await page.type('input[name="password"]', 'admin123');
      await page.click('button[type="submit"]');
      
      // 等待登录完成
      await page.waitForTimeout(3000);
      
      // 检查是否跳转到仪表板
      const currentUrl = page.url();
      console.log('🔗 当前URL:', currentUrl);
      
      if (currentUrl.includes('/dashboard')) {
        console.log('✅ 登录成功，已跳转到仪表板');
      }
    } else if (dashboard) {
      console.log('✅ 检测到仪表板页面');
    } else {
      console.log('⚠️ 未检测到预期的页面元素');
    }
    
    // 检查是否有JavaScript错误
    const jsErrors = await page.evaluate(() => {
      return window.jsErrors || [];
    });
    
    if (jsErrors.length > 0) {
      console.log('❌ JavaScript错误:', jsErrors);
      return false;
    }
    
    console.log('✅ 前端测试完成，页面正常加载');
    return true;
    
  } catch (error) {
    console.log('❌ 测试失败:', error.message);
    return false;
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// 运行测试
testFrontend().then(success => {
  if (success) {
    console.log('🎉 前端测试通过！');
    process.exit(0);
  } else {
    console.log('💥 前端测试失败！');
    process.exit(1);
  }
}).catch(error => {
  console.log('💥 测试运行失败:', error);
  process.exit(1);
});
