// Import commands.js using ES2015 syntax:
import './commands';

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Import cypress-axe for accessibility testing
import 'cypress-axe';

// Global configuration
Cypress.on('uncaught:exception', (err, runnable) => {
  // Returning false here prevents Cypress from failing the test
  // on uncaught exceptions. You might want to be more specific
  // about which exceptions to ignore.
  if (err.message.includes('ResizeObserver loop limit exceeded')) {
    return false;
  }
  if (err.message.includes('Non-Error promise rejection captured')) {
    return false;
  }
  return true;
});

// Set up global before hooks
beforeEach(() => {
  // Clear localStorage and sessionStorage before each test
  cy.clearLocalStorage();
  cy.clearCookies();
  
  // Set up common API interceptors
  cy.intercept('GET', '/api/courses/**').as('getCourses');
  cy.intercept('POST', '/api/courses/**').as('createCourse');
  cy.intercept('PUT', '/api/courses/**').as('updateCourse');
  cy.intercept('DELETE', '/api/courses/**').as('deleteCourse');
  
  cy.intercept('GET', '/api/users/**').as('getUsers');
  cy.intercept('POST', '/api/users/**').as('createUser');
  cy.intercept('PUT', '/api/users/**').as('updateUser');
  cy.intercept('DELETE', '/api/users/**').as('deleteUser');
  
  cy.intercept('GET', '/api/classrooms/**').as('getClassrooms');
  cy.intercept('POST', '/api/classrooms/**').as('createClassroom');
  cy.intercept('PUT', '/api/classrooms/**').as('updateClassroom');
  cy.intercept('DELETE', '/api/classrooms/**').as('deleteClassroom');
  
  // Set viewport to desktop by default
  cy.viewport(1280, 720);
});

// Global after hooks
afterEach(() => {
  // Take screenshot on failure
  cy.on('fail', (err) => {
    cy.screenshotWithTimestamp('failure');
    throw err;
  });
});

// Add custom Cypress configuration
Cypress.config('defaultCommandTimeout', 10000);
Cypress.config('requestTimeout', 10000);
Cypress.config('responseTimeout', 10000);

// Add support for data-testid selectors
Cypress.Commands.overwrite('contains', (originalFn, subject, filter, text, options = {}) => {
  if (typeof text === 'object') {
    options = text;
    text = filter;
    filter = undefined;
  }

  options.matchCase = false;
  return originalFn(subject, filter, text, options);
});

// Add custom matchers
chai.use((chai, utils) => {
  chai.Assertion.addMethod('haveTestId', function (testId) {
    const obj = this._obj;
    const hasTestId = obj.attr('data-testid') === testId;
    
    this.assert(
      hasTestId,
      `expected element to have data-testid "${testId}"`,
      `expected element not to have data-testid "${testId}"`,
      testId,
      obj.attr('data-testid')
    );
  });
});

// Performance monitoring
let performanceMarks: { [key: string]: number } = {};

Cypress.Commands.add('startPerformanceMark', (name: string) => {
  performanceMarks[name] = Date.now();
});

Cypress.Commands.add('endPerformanceMark', (name: string, maxDuration = 5000) => {
  const startTime = performanceMarks[name];
  if (startTime) {
    const duration = Date.now() - startTime;
    expect(duration).to.be.lessThan(maxDuration);
    delete performanceMarks[name];
  }
});

// Network monitoring
let networkRequests: any[] = [];

Cypress.Commands.add('startNetworkMonitoring', () => {
  networkRequests = [];
  cy.intercept('**', (req) => {
    networkRequests.push({
      method: req.method,
      url: req.url,
      timestamp: Date.now(),
    });
    req.continue();
  });
});

Cypress.Commands.add('getNetworkRequests', () => {
  return cy.wrap(networkRequests);
});

// Accessibility testing setup
Cypress.Commands.add('injectAxe', () => {
  cy.window({ log: false }).then((win) => {
    const script = win.document.createElement('script');
    script.src = 'https://unpkg.com/axe-core@4.4.3/axe.min.js';
    win.document.head.appendChild(script);
  });
});

// Visual regression testing helpers
Cypress.Commands.add('compareSnapshot', (name: string) => {
  cy.get('body').should('be.visible');
  cy.wait(500); // Wait for animations to complete
  cy.matchImageSnapshot(name);
});

// Database helpers for testing
Cypress.Commands.add('resetDatabase', () => {
  cy.task('db:reset');
});

Cypress.Commands.add('seedDatabase', (fixture: string) => {
  cy.task('db:seed', fixture);
});

// File upload helpers
Cypress.Commands.add('uploadFile', (selector: string, fileName: string, fileType = 'text/plain') => {
  cy.get(selector).then((subject) => {
    cy.fixture(fileName, 'base64').then((content) => {
      const el = subject[0];
      const blob = Cypress.Blob.base64StringToBlob(content, fileType);
      const file = new File([blob], fileName, { type: fileType });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      el.files = dataTransfer.files;
      
      // Trigger change event
      cy.wrap(subject).trigger('change', { force: true });
    });
  });
});

// Wait for React to finish rendering
Cypress.Commands.add('waitForReact', () => {
  cy.window().should('have.property', 'React');
  cy.get('[data-reactroot]').should('exist');
});

// Custom command for testing responsive design
Cypress.Commands.add('testResponsive', (callback: () => void) => {
  const viewports = [
    { width: 320, height: 568 }, // iPhone SE
    { width: 768, height: 1024 }, // iPad
    { width: 1024, height: 768 }, // iPad Landscape
    { width: 1280, height: 720 }, // Desktop
    { width: 1920, height: 1080 }, // Large Desktop
  ];

  viewports.forEach((viewport) => {
    cy.viewport(viewport.width, viewport.height);
    callback();
  });
});

export {};
