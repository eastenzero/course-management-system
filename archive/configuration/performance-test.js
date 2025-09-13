// 性能测试脚本
// 在浏览器控制台中运行此脚本来测试性能优化效果

(function() {
  'use strict';

  console.log('🚀 开始性能测试...');

  // 1. 测试缓存系统
  function testCacheSystem() {
    console.log('\n📦 测试缓存系统...');
    
    if (window.apiCache) {
      // 测试缓存写入和读取
      const testData = { id: 1, name: 'Test Course', description: 'Test Description' };
      const cacheKey = 'test-course-1';
      
      console.time('Cache Write');
      window.apiCache.set(cacheKey, testData);
      console.timeEnd('Cache Write');
      
      console.time('Cache Read');
      const cachedData = window.apiCache.get(cacheKey);
      console.timeEnd('Cache Read');
      
      console.log('✅ 缓存测试完成:', cachedData ? '成功' : '失败');
      
      // 测试缓存统计
      const stats = window.apiCache.getStats();
      console.log('📊 缓存统计:', stats);
    } else {
      console.log('❌ 缓存系统未找到');
    }
  }

  // 2. 测试性能监控
  function testPerformanceMonitoring() {
    console.log('\n📈 测试性能监控...');
    
    if (window.PerformanceTracker) {
      // 测试性能标记
      window.PerformanceTracker.mark('test-start');
      
      // 模拟一些操作
      setTimeout(() => {
        window.PerformanceTracker.mark('test-end');
        const duration = window.PerformanceTracker.measure('test-operation', 'test-start', 'test-end');
        console.log('⏱️ 操作耗时:', duration + 'ms');
        
        const allMeasures = window.PerformanceTracker.getAllMeasures();
        console.log('📊 所有性能指标:', allMeasures);
      }, 100);
    } else {
      console.log('❌ 性能监控系统未找到');
    }
  }

  // 3. 测试内存使用
  function testMemoryUsage() {
    console.log('\n💾 测试内存使用...');
    
    if (performance.memory) {
      const memory = performance.memory;
      console.log('📊 内存使用情况:');
      console.log('  - 已使用:', (memory.usedJSHeapSize / 1024 / 1024).toFixed(2) + ' MB');
      console.log('  - 总分配:', (memory.totalJSHeapSize / 1024 / 1024).toFixed(2) + ' MB');
      console.log('  - 限制:', (memory.jsHeapSizeLimit / 1024 / 1024).toFixed(2) + ' MB');
    } else {
      console.log('❌ 内存信息不可用');
    }
  }

  // 4. 测试网络性能
  function testNetworkPerformance() {
    console.log('\n🌐 测试网络性能...');
    
    const startTime = performance.now();
    
    fetch('/api/health')
      .then(response => {
        const endTime = performance.now();
        const duration = endTime - startTime;
        console.log('🚀 API响应时间:', duration.toFixed(2) + 'ms');
        console.log('📡 响应状态:', response.status);
      })
      .catch(error => {
        console.log('❌ 网络请求失败:', error.message);
      });
  }

  // 5. 测试DOM性能
  function testDOMPerformance() {
    console.log('\n🏗️ 测试DOM性能...');
    
    const startTime = performance.now();
    
    // 创建大量DOM元素
    const container = document.createElement('div');
    container.style.display = 'none';
    document.body.appendChild(container);
    
    for (let i = 0; i < 1000; i++) {
      const element = document.createElement('div');
      element.textContent = `Element ${i}`;
      container.appendChild(element);
    }
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    console.log('🏗️ 创建1000个DOM元素耗时:', duration.toFixed(2) + 'ms');
    
    // 清理
    document.body.removeChild(container);
  }

  // 6. 测试路由性能
  function testRoutePerformance() {
    console.log('\n🛣️ 测试路由性能...');
    
    if (window.RoutePreloader) {
      const status = window.RoutePreloader.getPreloadStatus();
      console.log('📊 路由预加载状态:');
      console.log('  - 已预加载:', status.preloaded.length + ' 个路由');
      console.log('  - 预加载中:', status.pending.length + ' 个路由');
      console.log('  - 预加载列表:', status.preloaded);
    } else {
      console.log('❌ 路由预加载器未找到');
    }
  }

  // 7. 测试资源加载性能
  function testResourcePerformance() {
    console.log('\n📦 测试资源加载性能...');
    
    if (performance.getEntriesByType) {
      const resources = performance.getEntriesByType('resource');
      const totalResources = resources.length;
      const totalSize = resources.reduce((sum, resource) => {
        return sum + (resource.transferSize || 0);
      }, 0);
      
      console.log('📊 资源加载统计:');
      console.log('  - 总资源数:', totalResources);
      console.log('  - 总传输大小:', (totalSize / 1024).toFixed(2) + ' KB');
      
      // 分析最慢的资源
      const slowestResources = resources
        .filter(resource => resource.duration > 0)
        .sort((a, b) => b.duration - a.duration)
        .slice(0, 5);
      
      console.log('⏱️ 最慢的5个资源:');
      slowestResources.forEach((resource, index) => {
        console.log(`  ${index + 1}. ${resource.name.split('/').pop()} - ${resource.duration.toFixed(2)}ms`);
      });
    }
  }

  // 8. 生成性能报告
  function generatePerformanceReport() {
    console.log('\n📋 生成性能报告...');
    
    const navigation = performance.getEntriesByType('navigation')[0];
    if (navigation) {
      console.log('🚀 页面加载性能:');
      console.log('  - DNS查询:', navigation.domainLookupEnd - navigation.domainLookupStart + 'ms');
      console.log('  - TCP连接:', navigation.connectEnd - navigation.connectStart + 'ms');
      console.log('  - 请求响应:', navigation.responseEnd - navigation.requestStart + 'ms');
      console.log('  - DOM解析:', navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart + 'ms');
      console.log('  - 页面加载:', navigation.loadEventEnd - navigation.loadEventStart + 'ms');
      console.log('  - 总耗时:', navigation.loadEventEnd - navigation.navigationStart + 'ms');
    }
    
    // Core Web Vitals
    if (window.PerformanceObserver) {
      console.log('📊 Core Web Vitals:');
      
      // LCP (Largest Contentful Paint)
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        console.log('  - LCP:', lastEntry.startTime.toFixed(2) + 'ms');
      }).observe({ entryTypes: ['largest-contentful-paint'] });
      
      // FID (First Input Delay) - 需要用户交互
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          console.log('  - FID:', entry.processingStart - entry.startTime + 'ms');
        });
      }).observe({ entryTypes: ['first-input'] });
    }
  }

  // 运行所有测试
  function runAllTests() {
    console.log('🎯 运行所有性能测试...\n');
    
    testCacheSystem();
    testPerformanceMonitoring();
    testMemoryUsage();
    testNetworkPerformance();
    testDOMPerformance();
    testRoutePerformance();
    testResourcePerformance();
    
    setTimeout(() => {
      generatePerformanceReport();
      console.log('\n✅ 所有性能测试完成！');
    }, 1000);
  }

  // 导出测试函数到全局
  window.performanceTest = {
    runAll: runAllTests,
    cache: testCacheSystem,
    monitoring: testPerformanceMonitoring,
    memory: testMemoryUsage,
    network: testNetworkPerformance,
    dom: testDOMPerformance,
    routes: testRoutePerformance,
    resources: testResourcePerformance,
    report: generatePerformanceReport
  };

  console.log('📝 性能测试工具已加载！');
  console.log('💡 使用方法:');
  console.log('  - performanceTest.runAll() - 运行所有测试');
  console.log('  - performanceTest.cache() - 测试缓存系统');
  console.log('  - performanceTest.memory() - 测试内存使用');
  console.log('  - performanceTest.network() - 测试网络性能');
  console.log('  - performanceTest.report() - 生成性能报告');

  // 自动运行测试
  runAllTests();

})();
