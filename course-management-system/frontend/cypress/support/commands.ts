/// <reference types="cypress" />

declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to login with username and password
       * @example cy.login('admin', 'password123')
       */
      login(username: string, password: string): Chainable<void>;
      
      /**
       * Custom command to verify file download
       * @example cy.verifyDownload('courses.csv')
       */
      verifyDownload(filename: string): Chainable<void>;
      
      /**
       * Custom command to seed test data
       * @example cy.seedData('courses')
       */
      seedData(dataType: string): Chainable<void>;
      
      /**
       * Custom command to clean test data
       * @example cy.cleanData()
       */
      cleanData(): Chainable<void>;
      
      /**
       * Custom command to wait for API response
       * @example cy.waitForApi('@getCourses')
       */
      waitForApi(alias: string): Chainable<void>;
    }
  }
}

// Login command
Cypress.Commands.add('login', (username: string, password: string) => {
  cy.session([username, password], () => {
    cy.visit('/login');
    cy.get('[data-testid="username-input"]').type(username);
    cy.get('[data-testid="password-input"]').type(password);
    cy.get('[data-testid="login-button"]').click();
    
    // Wait for successful login
    cy.url().should('not.include', '/login');
    cy.window().its('localStorage.token').should('exist');
  });
});

// Verify download command
Cypress.Commands.add('verifyDownload', (filename: string) => {
  const downloadsFolder = Cypress.config('downloadsFolder');
  cy.readFile(`${downloadsFolder}/${filename}`).should('exist');
});

// Seed test data command
Cypress.Commands.add('seedData', (dataType: string) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/test/seed/${dataType}/`,
    headers: {
      'Authorization': `Bearer ${window.localStorage.getItem('token')}`,
    },
  }).then((response) => {
    expect(response.status).to.eq(200);
  });
});

// Clean test data command
Cypress.Commands.add('cleanData', () => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/test/clean/`,
    headers: {
      'Authorization': `Bearer ${window.localStorage.getItem('token')}`,
    },
  }).then((response) => {
    expect(response.status).to.eq(200);
  });
});

// Wait for API command
Cypress.Commands.add('waitForApi', (alias: string) => {
  cy.wait(alias).then((interception) => {
    expect(interception.response?.statusCode).to.be.oneOf([200, 201, 204]);
  });
});

// Add data-testid attribute helper
Cypress.Commands.overwrite('get', (originalFn, selector, options) => {
  if (selector.startsWith('[data-testid=')) {
    return originalFn(selector, options);
  }
  
  // If selector doesn't start with [data-testid=, use original behavior
  return originalFn(selector, options);
});

// Custom assertion for checking table data
Cypress.Commands.add('checkTableData', (expectedData: any[]) => {
  cy.get('[data-testid="course-table"] tbody tr').should('have.length', expectedData.length);
  
  expectedData.forEach((item, index) => {
    cy.get('[data-testid="course-table"] tbody tr').eq(index).within(() => {
      if (item.name) {
        cy.contains(item.name).should('exist');
      }
      if (item.code) {
        cy.contains(item.code).should('exist');
      }
      if (item.department) {
        cy.contains(item.department).should('exist');
      }
    });
  });
});

// Custom command for handling form validation
Cypress.Commands.add('checkFormValidation', (fieldTestId: string, errorMessage: string) => {
  cy.get(`[data-testid="${fieldTestId}"]`).clear();
  cy.get('[data-testid="submit-button"]').click();
  cy.get(`[data-testid="${fieldTestId}-error"]`).should('contain', errorMessage);
});

// Custom command for API mocking
Cypress.Commands.add('mockApiResponse', (method: string, url: string, response: any, statusCode = 200) => {
  cy.intercept(method, url, {
    statusCode,
    body: response,
  }).as(`mock${method}${url.replace(/[^a-zA-Z0-9]/g, '')}`);
});

// Custom command for checking accessibility
Cypress.Commands.add('checkA11y', () => {
  cy.injectAxe();
  cy.checkA11y();
});

// Custom command for taking screenshots with timestamp
Cypress.Commands.add('screenshotWithTimestamp', (name: string) => {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  cy.screenshot(`${name}-${timestamp}`);
});

// Custom command for waiting for element to be stable
Cypress.Commands.add('waitForStable', (selector: string, timeout = 5000) => {
  let previousPosition: any = null;
  
  cy.get(selector, { timeout }).then(($el) => {
    const checkStability = () => {
      const currentPosition = $el.offset();
      
      if (previousPosition && 
          currentPosition?.top === previousPosition.top && 
          currentPosition?.left === previousPosition.left) {
        return; // Element is stable
      }
      
      previousPosition = currentPosition;
      cy.wait(100).then(checkStability);
    };
    
    checkStability();
  });
});

export {};
