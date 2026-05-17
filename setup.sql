-- ============================================================
-- Student Result Management System — Database Setup
-- Run this in MySQL BEFORE starting the Flask app
-- OR visit /init_db route after starting the app
-- ============================================================

CREATE DATABASE IF NOT EXISTS srms_db;
USE srms_db;

-- ── STUDENTS ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    hallticket  VARCHAR(20) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    password    VARCHAR(100) NOT NULL
);

-- ── FACULTY ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id  VARCHAR(20) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    password    VARCHAR(100) NOT NULL
);

-- ── FACULTY SUBJECT ASSIGNMENTS ───────────────────────────────
CREATE TABLE IF NOT EXISTS faculty_subjects (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id   VARCHAR(20),
    subject_code VARCHAR(20),
    subject_name VARCHAR(100),
    year         INT,
    semester     INT,
    UNIQUE KEY unique_subject (subject_code, semester),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE
);

-- ── SEMESTER RESULTS ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS semester_results (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    student_id     VARCHAR(20),
    subject_code   VARCHAR(20),
    subject_name   VARCHAR(100),
    credits        INT DEFAULT 3,
    internal_marks FLOAT DEFAULT 0,
    external_marks FLOAT DEFAULT 0,
    total_marks    FLOAT DEFAULT 0,
    grade          VARCHAR(5),
    grade_point    FLOAT DEFAULT 0,
    year           INT,
    semester       INT,
    exam_date      DATE,
    UNIQUE KEY unique_result (student_id, subject_code, year, semester),
    FOREIGN KEY (student_id) REFERENCES students(hallticket) ON DELETE CASCADE
);

-- ── INTERNAL MARKS ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS internal_marks (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id      VARCHAR(20),
    subject_code    VARCHAR(20),
    mid1_exam       FLOAT DEFAULT 0,
    mid1_assignment FLOAT DEFAULT 0,
    mid1_ppt        FLOAT DEFAULT 0,
    mid2_exam       FLOAT DEFAULT 0,
    mid2_assignment FLOAT DEFAULT 0,
    mid2_ppt        FLOAT DEFAULT 0,
    UNIQUE KEY unique_internal (student_id, subject_code),
    FOREIGN KEY (student_id) REFERENCES students(hallticket) ON DELETE CASCADE
);

-- ── SAMPLE DATA ───────────────────────────────────────────────
INSERT IGNORE INTO students VALUES
    ('22BD1A0501', 'Alice Johnson',  '22BD1A0501'),
    ('22BD1A0502', 'Bob Smith',      '22BD1A0502'),
    ('22BD1A0503', 'Carol Davis',    '22BD1A0503'),
    ('22BD1A0504', 'David Wilson',   '22BD1A0504'),
    ('22BD1A0505', 'Eva Martinez',   '22BD1A0505');

INSERT IGNORE INTO faculty VALUES
    ('F001', 'Dr. Ramesh Kumar', 'F001'),
    ('F002', 'Prof. Sunita Rao', 'F002'),
    ('F003', 'Dr. Arjun Mehta',  'F003');

INSERT IGNORE INTO faculty_subjects (faculty_id, subject_code, subject_name, year, semester) VALUES
    ('F001', 'CS301', 'Data Structures',      3, 1),
    ('F001', 'CS302', 'Design & Analysis of Algorithms', 3, 1),
    ('F002', 'CS303', 'Database Management Systems', 3, 1),
    ('F002', 'CS304', 'Operating Systems',   3, 1),
    ('F003', 'CS305', 'Computer Networks',   3, 1);

-- Sample results for Alice (a few backlogs for testing)
INSERT IGNORE INTO semester_results
    (student_id, subject_code, subject_name, credits, internal_marks, external_marks, total_marks, grade, grade_point, year, semester, exam_date)
VALUES
    ('22BD1A0501','CS301','Data Structures',             4, 25, 62, 87, 'A+', 9, 3, 1, '2024-11-20'),
    ('22BD1A0501','CS302','Design & Analysis of Algorithms', 4, 22, 45, 67, 'A',  8, 3, 1, '2024-11-22'),
    ('22BD1A0501','CS303','Database Management Systems', 3, 18, 20, 38, 'F',  0, 3, 1, '2024-11-24'),
    ('22BD1A0501','CS304','Operating Systems',           3, 20, 55, 75, 'B+', 7, 3, 1, '2024-11-26'),
    ('22BD1A0501','CS305','Computer Networks',           3, 15, 22, 37, 'F',  0, 3, 1, '2024-11-28');

-- Sample results for Bob
INSERT IGNORE INTO semester_results
    (student_id, subject_code, subject_name, credits, internal_marks, external_marks, total_marks, grade, grade_point, year, semester, exam_date)
VALUES
    ('22BD1A0502','CS301','Data Structures',             4, 28, 65, 93, 'O',  10, 3, 1, '2024-11-20'),
    ('22BD1A0502','CS302','Design & Analysis of Algorithms', 4, 26, 60, 86, 'A+', 9, 3, 1, '2024-11-22'),
    ('22BD1A0502','CS303','Database Management Systems', 3, 24, 58, 82, 'A+', 9, 3, 1, '2024-11-24'),
    ('22BD1A0502','CS304','Operating Systems',           3, 22, 52, 74, 'B+', 7, 3, 1, '2024-11-26'),
    ('22BD1A0502','CS305','Computer Networks',           3, 25, 55, 80, 'A+', 9, 3, 1, '2024-11-28');

-- Sample internal marks
INSERT IGNORE INTO internal_marks
    (student_id, subject_code, mid1_exam, mid1_assignment, mid1_ppt, mid2_exam, mid2_assignment, mid2_ppt)
VALUES
    ('22BD1A0501','CS301', 20, 4, 4, 22, 4, 5),
    ('22BD1A0501','CS302', 18, 3, 3, 20, 4, 4),
    ('22BD1A0501','CS303', 12, 3, 2, 14, 3, 3),
    ('22BD1A0502','CS301', 24, 5, 5, 25, 5, 5),
    ('22BD1A0502','CS302', 22, 5, 4, 23, 5, 5);

SELECT 'Database setup complete!' AS status;
