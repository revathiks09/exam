-- ============================================
-- ExamEase Database Setup Script
-- ============================================
-- Run this script in your MySQL 'examease' database
-- to create admin user and sample data
-- ============================================

-- 1. CREATE ADMIN USER
-- ============================================
INSERT INTO users (name, email, password, role, status, created_at) 
VALUES ('Admin User', 'admin@examease.com', 'admin123', 'admin', 1, NOW());

-- 2. CREATE SAMPLE DEPARTMENTS
-- ============================================
INSERT INTO departments (dept_name, status) VALUES
('Computer Science', 1),
('Electronics & Communication', 1),
('Mechanical Engineering', 1),
('Civil Engineering', 1),
('Information Technology', 1),
('Electrical Engineering', 1);

-- 3. CREATE SAMPLE COURSES
-- ============================================
INSERT INTO courses (dept_id, course_name, status) VALUES
(1, 'B.Tech Computer Science', 1),
(2, 'B.Tech Electronics & Communication', 1),
(3, 'B.Tech Mechanical Engineering', 1),
(4, 'B.Tech Civil Engineering', 1),
(5, 'B.Tech Information Technology', 1),
(6, 'B.Tech Electrical Engineering', 1),
(1, 'M.Tech Computer Science', 1),
(5, 'M.Tech Information Technology', 1);

-- 4. CREATE SAMPLE SEMESTERS (for B.Tech CS - course_id = 1)
-- ============================================
INSERT INTO semesters (course_id, semester_no) VALUES
(1, 1), (1, 2), (1, 3), (1, 4),
(1, 5), (1, 6), (1, 7), (1, 8);

-- 5. CREATE SAMPLE SEMESTERS (for B.Tech ECE - course_id = 2)
-- ============================================
INSERT INTO semesters (course_id, semester_no) VALUES
(2, 1), (2, 2), (2, 3), (2, 4),
(2, 5), (2, 6), (2, 7), (2, 8);

-- 6. CREATE SAMPLE FACULTY USERS
-- ============================================
INSERT INTO users (name, email, password, role, status, created_at) VALUES
('Dr. John Smith', 'john.smith@examease.com', 'faculty123', 'faculty', 1, NOW()),
('Dr. Sarah Johnson', 'sarah.johnson@examease.com', 'faculty123', 'faculty', 1, NOW()),
('Prof. Michael Brown', 'michael.brown@examease.com', 'faculty123', 'faculty', 1, NOW()),
('Dr. Emily Davis', 'emily.davis@examease.com', 'faculty123', 'faculty', 1, NOW()),
('Prof. David Wilson', 'david.wilson@examease.com', 'faculty123', 'faculty', 1, NOW());

-- 7. CREATE SAMPLE STUDENT USERS
-- ============================================
INSERT INTO users (name, email, password, role, status, created_at) VALUES
('Alice Williams', 'alice.williams@student.com', 'student123', 'student', 1, NOW()),
('Bob Davis', 'bob.davis@student.com', 'student123', 'student', 1, NOW()),
('Charlie Wilson', 'charlie.wilson@student.com', 'student123', 'student', 1, NOW()),
('Diana Martinez', 'diana.martinez@student.com', 'student123', 'student', 1, NOW()),
('Eve Anderson', 'eve.anderson@student.com', 'student123', 'student', 1, NOW()),
('Frank Thomas', 'frank.thomas@student.com', 'student123', 'student', 1, NOW()),
('Grace Taylor', 'grace.taylor@student.com', 'student123', 'student', 1, NOW()),
('Henry Moore', 'henry.moore@student.com', 'student123', 'student', 1, NOW()),
('Iris Jackson', 'iris.jackson@student.com', 'student123', 'student', 1, NOW()),
('Jack White', 'jack.white@student.com', 'student123', 'student', 1, NOW());

-- 8. CREATE SAMPLE EVALUATOR USERS
-- ============================================
INSERT INTO users (name, email, password, role, status, created_at) VALUES
('Dr. Robert Taylor', 'robert.taylor@examease.com', 'eval123', 'evaluator', 1, NOW()),
('Dr. Linda Thomas', 'linda.thomas@examease.com', 'eval123', 'evaluator', 1, NOW()),
('Dr. James Harris', 'james.harris@examease.com', 'eval123', 'evaluator', 1, NOW());

-- ============================================
-- VERIFICATION QUERIES
-- ============================================
-- Run these to verify the data was inserted correctly

-- Check total users by role
SELECT role, COUNT(*) as count FROM users GROUP BY role;

-- Check departments
SELECT * FROM departments;

-- Check courses with departments
SELECT c.id, c.course_name, d.dept_name, c.status 
FROM courses c 
LEFT JOIN departments d ON c.dept_id = d.id;

-- Check semesters with courses
SELECT s.id, c.course_name, s.semester_no 
FROM semesters s 
LEFT JOIN courses c ON s.course_id = c.id;

-- ============================================
-- LOGIN CREDENTIALS
-- ============================================
-- Admin:
--   Email: admin@examease.com
--   Password: admin123
--
-- Faculty:
--   Email: john.smith@examease.com
--   Password: faculty123
--
-- Student:
--   Email: alice.williams@student.com
--   Password: student123
--
-- Evaluator:
--   Email: robert.taylor@examease.com
--   Password: eval123
-- ============================================
