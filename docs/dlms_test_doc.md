# DLMS Testing Documentation

## Testing Strategy
This document outlines comprehensive testing procedures for the Distance Learning Management System following the Waterfall SDLC methodology.

## Test Environment
- **Operating System:** Windows/macOS/Linux
- **Python Version:** 3.7+
- **MySQL Version:** 5.7+
- **Browser:** Chrome 90+, Firefox 88+, Safari 14+

---

## 1. Unit Testing

### 1.1 Authentication Module Tests

#### Test Case 1.1.1: Valid Login - Administrator
**Objective:** Verify administrator can log in with correct credentials  
**Prerequisites:** Database is set up with default admin account  
**Test Steps:**
1. Navigate to http://127.0.0.1:5000/login
2. Enter email: admin@dlms.com
3. Enter password: admin123
4. Click "Login" button

**Expected Result:**
- User is redirected to administrator dashboard
- Welcome message displays "Welcome, System Administrator!"
- Navigation shows role as "Administrator"

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 1.1.2: Valid Login - Lecturer
**Objective:** Verify lecturer can log in with correct credentials  
**Test Steps:**
1. Navigate to login page
2. Enter email: lecturer@dlms.com
3. Enter password: lecturer123
4. Click "Login"

**Expected Result:**
- Redirect to lecturer dashboard
- Displays lecturer-specific menu options

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 1.1.3: Valid Login - Student
**Objective:** Verify student can log in with correct credentials  
**Test Steps:**
1. Navigate to login page
2. Enter email: student@dlms.com
3. Enter password: student123
4. Click "Login"

**Expected Result:**
- Redirect to student dashboard
- Displays student-specific menu options

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 1.1.4: Invalid Login - Wrong Password
**Objective:** Verify system rejects incorrect password  
**Test Steps:**
1. Navigate to login page
2. Enter email: admin@dlms.com
3. Enter password: wrongpassword
4. Click "Login"

**Expected Result:**
- Login fails
- Error message: "Invalid email or password"
- User remains on login page

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 1.1.5: Invalid Login - Non-existent User
**Objective:** Verify system rejects non-existent users  
**Test Steps:**
1. Navigate to login page
2. Enter email: nonexistent@test.com
3. Enter password: anypassword
4. Click "Login"

**Expected Result:**
- Login fails
- Error message displayed
- User remains on login page

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 1.1.6: Login - Deactivated Account
**Objective:** Verify deactivated users cannot log in  
**Test Steps:**
1. Admin deactivates a user account
2. Attempt to login with deactivated account credentials

**Expected Result:**
- Login fails
- Message: "Your account has been deactivated"

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 1.1.7: Logout Functionality
**Objective:** Verify logout clears session  
**Test Steps:**
1. Log in as any user
2. Click "Logout" button
3. Attempt to access dashboard URL directly

**Expected Result:**
- User is logged out
- Session is cleared
- Redirect to login page with message
- Direct URL access denied

**Status:** ☐ Pass ☐ Fail

---

### 1.2 Role-Based Access Control Tests

#### Test Case 1.2.1: Student Access Restriction
**Objective:** Verify students cannot access admin/lecturer pages  
**Test Steps:**
1. Log in as student
2. Try to access /admin/dashboard directly
3. Try to access /lecturer/dashboard directly

**Expected Result:**
- Access denied
- Redirect to appropriate page
- Error message displayed

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 1.2.2: Lecturer Access Restriction
**Objective:** Verify lecturers cannot access admin pages  
**Test Steps:**
1. Log in as lecturer
2. Try to access /admin/users directly

**Expected Result:**
- Access denied
- Appropriate error message

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 1.2.3: Unauthenticated Access
**Objective:** Verify unauthenticated users cannot access protected pages  
**Test Steps:**
1. Ensure logged out
2. Try to access /admin/dashboard
3. Try to access /lecturer/courses
4. Try to access /student/courses

**Expected Result:**
- All attempts redirect to login page
- Message: "Please log in to access this page"

**Status:** ☐ Pass ☐ Fail

---

## 2. Administrator Module Tests

#### Test Case 2.1: Create User - Valid Data
**Objective:** Verify admin can create new users  
**Test Steps:**
1. Log in as administrator
2. Navigate to "Create User"
3. Enter full name: "Test Student"
4. Enter email: "teststudent@test.com"
5. Enter password: "password123"
6. Select role: "Student"
7. Click "Create User"

**Expected Result:**
- User created successfully
- Success message displayed
- User appears in user list
- Can log in with new credentials

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 2.2: Create User - Duplicate Email
**Objective:** Verify system prevents duplicate emails  
**Test Steps:**
1. Attempt to create user with existing email

**Expected Result:**
- Creation fails
- Error message: "Email already exists"

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 2.3: Create User - Missing Fields
**Objective:** Verify form validation  
**Test Steps:**
1. Navigate to create user form
2. Leave required fields empty
3. Attempt to submit

**Expected Result:**
- Form validation prevents submission
- Required field indicators appear

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 2.4: Toggle User Status
**Objective:** Verify admin can activate/deactivate users  
**Test Steps:**
1. View user list
2. Click "Deactivate" on active user
3. Verify status changes to "Inactive"
4. Click "Activate" on inactive user
5. Verify status changes to "Active"

**Expected Result:**
- Status toggles correctly
- Badge color changes
- Confirmation message displayed

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 2.5: View All Courses
**Objective:** Verify admin can view all courses  
**Test Steps:**
1. Navigate to "View All Courses"
2. Verify course list displays

**Expected Result:**
- All courses visible
- Shows course details and lecture count
- Displays lecturer names

**Status:** ☐ Pass ☐ Fail

---

## 3. Lecturer Module Tests

#### Test Case 3.1: Create Course - Valid Data
**Objective:** Verify lecturer can create courses  
**Test Steps:**
1. Log in as lecturer
2. Navigate to "Create Course"
3. Enter title: "Test Course"
4. Enter description: "This is a test course"
5. Click "Create Course"

**Expected Result:**
- Course created successfully
- Success message displayed
- Course appears in lecturer's course list

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 3.2: Create Course - Missing Fields
**Objective:** Verify form validation  
**Test Steps:**
1. Navigate to create course
2. Leave fields empty
3. Attempt submission

**Expected Result:**
- Form validation prevents submission
- Required fields highlighted

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 3.3: Upload Lecture - Valid Video
**Objective:** Verify lecturer can upload video lectures  
**Prerequisites:** At least one course exists  
**Test Steps:**
1. Navigate to "Upload Lecture"
2. Enter lecture title: "Introduction"
3. Enter description: "Course introduction"
4. Select a course
5. Upload valid MP4 file (under 100MB)
6. Click "Upload Lecture"

**Expected Result:**
- File uploads successfully
- Video saved in static/uploads/videos/
- Database entry created with file path
- Success message displayed
- Lecture appears in course lecture list

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 3.4: Upload Lecture - Invalid File Type
**Objective:** Verify system rejects invalid file types  
**Test Steps:**
1. Navigate to upload lecture
2. Attempt to upload .txt or .exe file

**Expected Result:**
- Upload rejected
- Error message: "Invalid file type"

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 3.5: Upload Lecture - File Too Large
**Objective:** Verify file size limit enforcement  
**Test Steps:**
1. Attempt to upload file over 100MB

**Expected Result:**
- Upload rejected
- Appropriate error message

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 3.6: Upload Lecture - No Course Created
**Objective:** Verify handling when no courses exist  
**Test Steps:**
1. New lecturer with no courses
2. Navigate to upload lecture

**Expected Result:**
- Warning message displayed
- Link to create course first

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 3.7: View Course Lectures
**Objective:** Verify lecturer can view their course lectures  
**Test Steps:**
1. Navigate to "My Courses"
2. Click "View Lectures" on a course

**Expected Result:**
- All lectures for that course displayed
- Shows lecture details and upload dates
- Option to upload more lectures

**Status:** ☐ Pass ☐ Fail

---

## 4. Student Module Tests

#### Test Case 4.1: View Available Courses
**Objective:** Verify student can browse courses  
**Test Steps:**
1. Log in as student
2. Navigate to "Enroll in Course"

**Expected Result:**
- Available courses displayed
- Shows course descriptions and instructors
- "Enroll Now" button visible

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 4.2: Enroll in Course
**Objective:** Verify student can enroll in courses  
**Test Steps:**
1. Navigate to "Enroll in Course"
2. Click "Enroll Now" on a course
3. Confirm enrollment

**Expected Result:**
- Enrollment successful
- Success message displayed
- Course appears in "My Courses"
- Course removed from available courses list

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 4.3: Duplicate Enrollment Prevention
**Objective:** Verify students cannot enroll twice  
**Test Steps:**
1. Enroll in a course
2. Attempt to enroll again

**Expected Result:**
- Second enrollment rejected
- Appropriate error message

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 4.4: View Enrolled Courses
**Objective:** Verify student can view enrolled courses  
**Test Steps:**
1. Navigate to "My Courses"

**Expected Result:**
- All enrolled courses displayed
- Shows course details and lecture count
- "View Lectures" button available

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 4.5: View Course Lectures
**Objective:** Verify student can view lectures for enrolled courses  
**Test Steps:**
1. Navigate to "My Courses"
2. Click "View Lectures" on enrolled course

**Expected Result:**
- All lectures for course displayed
- Shows lecture titles and descriptions
- "Watch Lecture" button available

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 4.6: Access Control - Non-enrolled Course
**Objective:** Verify students cannot access lectures from non-enrolled courses  
**Test Steps:**
1. Find lecture ID for non-enrolled course
2. Try to access URL directly: /student/lecture/{id}

**Expected Result:**
- Access denied
- Error message: "Access denied. You are not enrolled in this course"
- Redirect to courses page

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 4.7: Watch Video Lecture
**Objective:** Verify video streaming functionality  
**Test Steps:**
1. Navigate to enrolled course lectures
2. Click "Watch Lecture"
3. Verify video player loads
4. Click play button

**Expected Result:**
- Video page loads
- Video player embedded
- Video plays successfully
- Controls available (play, pause, volume)
- Download option disabled

**Status:** ☐ Pass ☐ Fail

---

## 5. Database Integration Tests

#### Test Case 5.1: Password Hashing
**Objective:** Verify passwords are hashed in database  
**Test Steps:**
1. Create a new user
2. Check database directly

**Expected Result:**
- Password stored as hash, not plain text
- Hash starts with "scrypt:" or "pbkdf2:"

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 5.2: Foreign Key Constraints
**Objective:** Verify referential integrity  
**Test Steps:**
1. Attempt to delete a lecturer with courses
2. Check if courses are handled appropriately

**Expected Result:**
- Cascade delete or appropriate error
- Database maintains integrity

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 5.3: Enrollment Unique Constraint
**Objective:** Verify unique enrollment constraint  
**Test Steps:**
1. Enroll student in course
2. Attempt duplicate enrollment via direct database insert

**Expected Result:**
- Duplicate rejected by database
- Unique constraint error

**Status:** ☐ Pass ☐ Fail

---

## 6. Security Tests

#### Test Case 6.1: SQL Injection Prevention
**Objective:** Verify system is protected against SQL injection  
**Test Steps:**
1. In login form, enter: admin@dlms.com' OR '1'='1
2. Attempt various SQL injection patterns

**Expected Result:**
- Login fails
- No SQL errors exposed
- Parameterized queries prevent injection

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 6.2: Session Security
**Objective:** Verify session cannot be hijacked  
**Test Steps:**
1. Log in and note session cookie
2. Log out
3. Try to reuse old session cookie

**Expected Result:**
- Session invalidated after logout
- Old session cookie rejected

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 6.3: File Upload Security
**Objective:** Verify malicious file uploads are prevented  
**Test Steps:**
1. Attempt to upload .php or .exe file renamed as .mp4
2. Attempt to upload file with path traversal in name

**Expected Result:**
- Malicious files rejected
- Filename sanitized
- No code execution possible

**Status:** ☐ Pass ☐ Fail

---

## 7. UI/UX Tests

#### Test Case 7.1: Responsive Design
**Objective:** Verify layout adapts to screen size  
**Test Steps:**
1. View application on desktop (1920x1080)
2. View on tablet (768x1024)
3. View on mobile (375x667)

**Expected Result:**
- Layout adjusts appropriately
- All content accessible
- No horizontal scrolling

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 7.2: Flash Messages
**Objective:** Verify user feedback messages  
**Test Steps:**
1. Perform various actions (login, create user, etc.)
2. Verify appropriate messages appear

**Expected Result:**
- Success messages in green
- Error messages in red
- Warning messages in yellow
- Messages dismissible

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 7.3: Navigation Flow
**Objective:** Verify intuitive navigation  
**Test Steps:**
1. Navigate through all pages as each role
2. Verify back buttons work correctly

**Expected Result:**
- Clear navigation paths
- Back buttons return to appropriate pages
- No broken links

**Status:** ☐ Pass ☐ Fail

---

## 8. Performance Tests

#### Test Case 8.1: Page Load Time
**Objective:** Verify acceptable page load times  
**Test Steps:**
1. Clear browser cache
2. Load various pages
3. Measure load time

**Expected Result:**
- Pages load within 2 seconds
- Database queries optimized

**Status:** ☐ Pass ☐ Fail

---

#### Test Case 8.2: Video Streaming Performance
**Objective:** Verify smooth video playback  
**Test Steps:**
1. Stream various video files
2. Check for buffering issues

**Expected Result:**
- Videos stream without excessive buffering
- Playback smooth for files under 100MB

**Status:** ☐ Pass ☐ Fail

---

## 9. Integration Tests

#### Test Case 9.1: End-to-End Workflow - Course Creation to Viewing
**Objective:** Verify complete workflow  
**Test Steps:**
1. Admin creates lecturer account
2. Lecturer logs in and creates course
3. Lecturer uploads video lecture
4. Admin creates student account
5. Student logs in and enrolls in course
6. Student views and watches lecture

**Expected Result:**
- All steps complete successfully
- Data flows correctly between components
- Video accessible to enrolled student

**Status:** ☐ Pass ☐ Fail

---

## Test Summary Report

### Test Execution Summary
- **Total Test Cases:** 45
- **Passed:** ___
- **Failed:** ___
- **Blocked:** ___
- **Not Executed:** ___

### Critical Issues Found
1. _______________
2. _______________
3. _______________

### Recommendations
1. _______________
2. _______________
3. _______________

### Sign-off
- **Tested By:** _______________
- **Date:** _______________
- **Status:** ☐ Approved ☐ Rejected ☐ Conditional Approval

---

## Notes for Testers
- Always test with fresh database for consistent results
- Document any unexpected behavior
- Take screenshots of errors
- Note browser and OS version for any issues
- Verify all test prerequisites before starting
- Report security issues immediately
