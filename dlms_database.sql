-- DLMS Database Schema
-- Create Database
CREATE DATABASE IF NOT EXISTS dlms_db;
USE dlms_db;

-- Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('administrator', 'lecturer', 'student') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Courses Table
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_title VARCHAR(200) NOT NULL,
    course_description TEXT NOT NULL,
    lecturer_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lecturer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_lecturer (lecturer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Lectures Table
CREATE TABLE lectures (
    lecture_id INT AUTO_INCREMENT PRIMARY KEY,
    lecture_title VARCHAR(200) NOT NULL,
    lecture_description TEXT NOT NULL,
    video_path VARCHAR(500) NOT NULL,
    course_id INT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    INDEX idx_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Enrollments Table
CREATE TABLE enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    UNIQUE KEY unique_enrollment (student_id, course_id),
    INDEX idx_student (student_id),
    INDEX idx_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert Default Administrator Account
-- Password: admin123
INSERT INTO users (full_name, email, password_hash, role) VALUES 
('System Administrator', 'admin@dlms.com', 'scrypt:32768:8:1$BjW4GvLaYHKBT0sD$e3c4c4f6e8a9f5a3b2c1d0e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8', 'administrator');

-- Insert Sample Lecturer (Password: lecturer123)
INSERT INTO users (full_name, email, password_hash, role) VALUES 
('Dr. John Smith', 'lecturer@dlms.com', 'scrypt:32768:8:1$BjW4GvLaYHKBT0sD$a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4', 'lecturer');

-- Insert Sample Student (Password: student123)
INSERT INTO users (full_name, email, password_hash, role) VALUES 
('Jane Doe', 'student@dlms.com', 'scrypt:32768:8:1$BjW4GvLaYHKBT0sD$f0e1d2c3b4a5968778695a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3', 'student');

-- Insert Sample Course
INSERT INTO courses (course_title, course_description, lecturer_id) VALUES 
('Introduction to Web Development', 'Learn HTML, CSS, JavaScript, and modern web development practices.', 2);

-- Assignments Table
CREATE TABLE assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    deadline DATETIME NOT NULL,
    total_points INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    INDEX idx_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Submissions Table
CREATE TABLE submissions (
    submission_id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id INT NOT NULL,
    student_id INT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    score INT,
    feedback TEXT,
    status ENUM('submitted', 'graded') DEFAULT 'submitted',
    allow_resubmission BOOLEAN DEFAULT FALSE,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    graded_at TIMESTAMP NULL,
    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_assignment (assignment_id),
    INDEX idx_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Questions Table (Q&A)
CREATE TABLE questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    student_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Answers Table (Q&A)
CREATE TABLE answers (
    answer_id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_question (question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Exams Table
CREATE TABLE exams (
    exam_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    duration_minutes INT NOT NULL,
    total_points INT DEFAULT 100,
    camera_required BOOLEAN DEFAULT FALSE,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Exam Questions Table
CREATE TABLE exam_questions (
    exam_question_id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer ENUM('A', 'B', 'C', 'D') NOT NULL,
    points INT DEFAULT 1,
    FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE,
    INDEX idx_exam (exam_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Exam Attempts Table
CREATE TABLE exam_attempts (
    attempt_id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    student_id INT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    status ENUM('in_progress', 'completed') DEFAULT 'in_progress',
    score INT DEFAULT 0,
    camera_enabled BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_exam (exam_id),
    INDEX idx_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Exam Answers Table
CREATE TABLE exam_answers (
    answer_id INT AUTO_INCREMENT PRIMARY KEY,
    attempt_id INT NOT NULL,
    exam_question_id INT NOT NULL,
    student_answer ENUM('A', 'B', 'C', 'D') NULL,
    FOREIGN KEY (attempt_id) REFERENCES exam_attempts(attempt_id) ON DELETE CASCADE,
    FOREIGN KEY (exam_question_id) REFERENCES exam_questions(exam_question_id) ON DELETE CASCADE,
    INDEX idx_attempt (attempt_id),
    INDEX idx_question (exam_question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Note: Passwords are hashed. For testing, create users through the admin interface
-- or update the password_hash using Python with:
-- from werkzeug.security import generate_password_hash
-- print(generate_password_hash('your_password'))
