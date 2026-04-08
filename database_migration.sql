-- Database Migration: Add CASCADE DELETE constraints
-- This script adds missing ON DELETE CASCADE constraints to ensure data integrity
-- Run this script to update the database schema

USE dlms_db;

-- Drop existing constraints that don't have CASCADE
ALTER TABLE questions DROP FOREIGN KEY questions_ibfk_1;
ALTER TABLE questions DROP FOREIGN KEY questions_ibfk_2;
ALTER TABLE answers DROP FOREIGN KEY answers_ibfk_1;
ALTER TABLE answers DROP FOREIGN KEY answers_ibfk_2;
ALTER TABLE assignments DROP FOREIGN KEY assignments_ibfk_1;
ALTER TABLE assignments DROP FOREIGN KEY assignments_ibfk_2;
ALTER TABLE submissions DROP FOREIGN KEY submissions_ibfk_1;
ALTER TABLE submissions DROP FOREIGN KEY submissions_ibfk_2;
ALTER TABLE exams DROP FOREIGN KEY exams_ibfk_1;
ALTER TABLE exams DROP FOREIGN KEY exams_ibfk_2;
ALTER TABLE exam_attempts DROP FOREIGN KEY exam_attempts_ibfk_1;
ALTER TABLE exam_attempts DROP FOREIGN KEY exam_attempts_ibfk_2;

-- Recreate constraints with CASCADE
ALTER TABLE questions ADD CONSTRAINT questions_ibfk_1 FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE;
ALTER TABLE questions ADD CONSTRAINT questions_ibfk_2 FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE;
ALTER TABLE answers ADD CONSTRAINT answers_ibfk_1 FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE;
ALTER TABLE answers ADD CONSTRAINT answers_ibfk_2 FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
ALTER TABLE assignments ADD CONSTRAINT assignments_ibfk_1 FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE;
ALTER TABLE assignments ADD CONSTRAINT assignments_ibfk_2 FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE;
ALTER TABLE submissions ADD CONSTRAINT submissions_ibfk_1 FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id) ON DELETE CASCADE;
ALTER TABLE submissions ADD CONSTRAINT submissions_ibfk_2 FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE;
ALTER TABLE exams ADD CONSTRAINT exams_ibfk_1 FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE;
ALTER TABLE exams ADD CONSTRAINT exams_ibfk_2 FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE;
ALTER TABLE exam_attempts ADD CONSTRAINT exam_attempts_ibfk_1 FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE;
ALTER TABLE exam_attempts ADD CONSTRAINT exam_attempts_ibfk_2 FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE;

-- Note: The following tables already have CASCADE constraints:
-- - courses (lecturer_id -> users)
-- - enrollments (student_id -> users, course_id -> courses)
-- - lectures (course_id -> courses)