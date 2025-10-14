describe('Course Management E2E Tests', () => {
  beforeEach(() => {
    // Login as admin before each test
    cy.login('admin', 'admin123');
    cy.visit('/courses');
  });

  it('should display course list page', () => {
    cy.get('[data-testid="page-title"]').should('contain', '课程管理');
    cy.get('[data-testid="course-table"]').should('be.visible');
  });

  it('should search for courses', () => {
    // Type in search input
    cy.get('[data-testid="search-input"]').type('计算机');
    
    // Click search button
    cy.get('[data-testid="search-button"]').click();
    
    // Verify search results
    cy.get('[data-testid="course-table"]').should('contain', '计算机');
  });

  it('should filter courses by department', () => {
    // Open department filter
    cy.get('[data-testid="department-filter"]').click();
    
    // Select a department
    cy.get('[data-testid="department-option-cs"]').click();
    
    // Click search
    cy.get('[data-testid="search-button"]').click();
    
    // Verify filtered results
    cy.get('[data-testid="course-table"]').should('contain', '计算机学院');
  });

  it('should create a new course', () => {
    // Click add course button
    cy.get('[data-testid="add-course-button"]').click();
    
    // Fill course form
    cy.get('[data-testid="course-name-input"]').type('新课程');
    cy.get('[data-testid="course-code-input"]').type('NEW101');
    cy.get('[data-testid="course-credits-input"]').type('3');
    cy.get('[data-testid="course-department-select"]').click();
    cy.get('[data-testid="department-option-cs"]').click();
    
    // Submit form
    cy.get('[data-testid="submit-button"]').click();
    
    // Verify success message
    cy.get('[data-testid="success-message"]').should('contain', '课程创建成功');
    
    // Verify course appears in list
    cy.visit('/courses');
    cy.get('[data-testid="course-table"]').should('contain', '新课程');
  });

  it('should edit an existing course', () => {
    // Click edit button for first course
    cy.get('[data-testid="edit-course-button"]').first().click();
    
    // Update course name
    cy.get('[data-testid="course-name-input"]').clear().type('更新的课程名称');
    
    // Submit form
    cy.get('[data-testid="submit-button"]').click();
    
    // Verify success message
    cy.get('[data-testid="success-message"]').should('contain', '课程更新成功');
    
    // Verify updated name appears in list
    cy.visit('/courses');
    cy.get('[data-testid="course-table"]').should('contain', '更新的课程名称');
  });

  it('should delete a course', () => {
    // Click delete button for first course
    cy.get('[data-testid="delete-course-button"]').first().click();
    
    // Confirm deletion in dialog
    cy.get('[data-testid="confirm-delete-button"]').click();
    
    // Verify success message
    cy.get('[data-testid="success-message"]').should('contain', '课程删除成功');
  });

  it('should export course data', () => {
    // Click export dropdown
    cy.get('[data-testid="export-dropdown"]').click();
    
    // Click CSV export
    cy.get('[data-testid="export-csv-button"]').click();
    
    // Verify download (this would need custom command)
    cy.verifyDownload('courses.csv');
  });

  it('should handle pagination', () => {
    // Go to next page
    cy.get('[data-testid="pagination-next"]').click();
    
    // Verify page change
    cy.get('[data-testid="pagination-current"]').should('contain', '2');
    
    // Verify different data is loaded
    cy.get('[data-testid="course-table"]').should('be.visible');
  });

  it('should show course details', () => {
    // Click view button for first course
    cy.get('[data-testid="view-course-button"]').first().click();
    
    // Verify course detail page
    cy.url().should('include', '/courses/');
    cy.get('[data-testid="course-detail"]').should('be.visible');
  });

  it('should handle empty state', () => {
    // Search for non-existent course
    cy.get('[data-testid="search-input"]').type('不存在的课程');
    cy.get('[data-testid="search-button"]').click();
    
    // Verify empty state
    cy.get('[data-testid="empty-state"]').should('be.visible');
    cy.get('[data-testid="empty-state"]').should('contain', '没有找到课程');
  });

  it('should handle loading states', () => {
    // Intercept API call to add delay
    cy.intercept('GET', '/api/courses/', { delay: 2000 }).as('getCourses');
    
    // Reload page
    cy.reload();
    
    // Verify loading state
    cy.get('[data-testid="loading-spinner"]').should('be.visible');
    
    // Wait for API call
    cy.wait('@getCourses');
    
    // Verify loading state is gone
    cy.get('[data-testid="loading-spinner"]').should('not.exist');
  });

  it('should handle error states', () => {
    // Intercept API call to return error
    cy.intercept('GET', '/api/courses/', { statusCode: 500 }).as('getCoursesError');
    
    // Reload page
    cy.reload();
    
    // Wait for API call
    cy.wait('@getCoursesError');
    
    // Verify error message
    cy.get('[data-testid="error-message"]').should('contain', '获取课程列表失败');
  });
});

describe('Course Management Permissions', () => {
  it('should show limited actions for teacher role', () => {
    cy.login('teacher', 'teacher123');
    cy.visit('/courses');
    
    // Teacher should see view and edit buttons but not delete
    cy.get('[data-testid="view-course-button"]').should('exist');
    cy.get('[data-testid="edit-course-button"]').should('exist');
    cy.get('[data-testid="delete-course-button"]').should('not.exist');
  });

  it('should show read-only view for student role', () => {
    cy.login('student', 'student123');
    cy.visit('/courses');
    
    // Student should only see view buttons
    cy.get('[data-testid="view-course-button"]').should('exist');
    cy.get('[data-testid="edit-course-button"]').should('not.exist');
    cy.get('[data-testid="delete-course-button"]').should('not.exist');
    cy.get('[data-testid="add-course-button"]').should('not.exist');
  });
});

describe('Course Management Responsive Design', () => {
  it('should work on mobile devices', () => {
    cy.viewport('iphone-x');
    cy.visit('/courses');
    
    // Verify mobile layout
    cy.get('[data-testid="mobile-menu-button"]').should('be.visible');
    cy.get('[data-testid="course-table"]').should('be.visible');
  });

  it('should work on tablet devices', () => {
    cy.viewport('ipad-2');
    cy.visit('/courses');
    
    // Verify tablet layout
    cy.get('[data-testid="course-table"]').should('be.visible');
  });
});
