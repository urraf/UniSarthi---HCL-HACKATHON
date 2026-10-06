-- UniSarthi student data (synthetic, all persons fictitious)
-- Exported from backend/data/unisarthi.db (SQLite). Tables: courses, students, attendance, results, rule_registry.

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE students (
    student_id       TEXT PRIMARY KEY,      -- S + 4 digits, e.g. S1001
    full_name        TEXT NOT NULL,         -- synthetic names only
    programme        TEXT NOT NULL,         -- e.g. B.Tech CSE
    batch_year       INTEGER NOT NULL,      -- year of admission
    current_semester INTEGER NOT NULL,      -- 1-10
    cgpa             REAL NOT NULL,         -- 0.00-10.00
    active_backlogs  INTEGER NOT NULL,      -- >= 0
    roll_number      TEXT UNIQUE,           -- extra: university roll number, e.g. 2023UIT3015 (CSV column roll_no)
    email            TEXT                   -- extra: institute email (synthetic)
);
INSERT INTO students VALUES('S1001','Jatin Reddy','B.Tech IT',2023,7,8.5,0,'2023UIT3101','jatin.reddy.2023uit3101@nsut.ac.in');
INSERT INTO students VALUES('S1002','Saanvi Mishra','B.Tech IT',2023,7,6.9,1,'2023UIT3102','saanvi.mishra.2023uit3102@nsut.ac.in');
INSERT INTO students VALUES('S1003','Siddharth Nair','B.Tech IT',2023,7,6.4,1,'2023UIT3103','siddharth.nair.2023uit3103@nsut.ac.in');
INSERT INTO students VALUES('S1004','Tanvi Ahuja','B.Tech IT',2023,7,5.0,4,'2023UIT3104','tanvi.ahuja.2023uit3104@nsut.ac.in');
INSERT INTO students VALUES('S1005','Diya Rana','B.Tech IT',2023,7,7.5,0,'2023UIT3105','diya.rana.2023uit3105@nsut.ac.in');
INSERT INTO students VALUES('S1006','Varun Bansal','B.Tech IT',2023,7,7.1,0,'2023UIT3106','varun.bansal.2023uit3106@nsut.ac.in');
INSERT INTO students VALUES('S1007','Kavya Tiwari','B.Tech IT',2023,7,9.14,0,'2023UIT3107','kavya.tiwari.2023uit3107@nsut.ac.in');
INSERT INTO students VALUES('S1008','Arnav Iyer','B.Tech IT',2023,7,6.5,0,'2023UIT3108','arnav.iyer.2023uit3108@nsut.ac.in');
INSERT INTO students VALUES('S1009','Shreya Chauhan','B.Tech IT',2024,5,8.0,0,'2024UIT3101','shreya.chauhan.2024uit3101@nsut.ac.in');
INSERT INTO students VALUES('S1010','Neha Rawat','B.Tech IT',2024,5,8.85,0,'2024UIT3102','neha.rawat.2024uit3102@nsut.ac.in');
INSERT INTO students VALUES('S1011','Navya Dahiya','B.Tech IT',2024,5,8.67,0,'2024UIT3103','navya.dahiya.2024uit3103@nsut.ac.in');
INSERT INTO students VALUES('S1012','Kabir Tomar','B.Tech IT',2024,5,7.5,0,'2024UIT3104','kabir.tomar.2024uit3104@nsut.ac.in');
INSERT INTO students VALUES('S1013','Meera Bhatia','B.Tech IT',2024,5,7.0,0,'2024UIT3105','meera.bhatia.2024uit3105@nsut.ac.in');
INSERT INTO students VALUES('S1014','Riya Pandey','B.Tech IT',2024,5,6.6,1,'2024UIT3106','riya.pandey.2024uit3106@nsut.ac.in');
INSERT INTO students VALUES('S1015','Lakshya Yadav','B.Tech IT',2024,5,8.4,0,'2024UIT3107','lakshya.yadav.2024uit3107@nsut.ac.in');
INSERT INTO students VALUES('S1016','Mohit Saxena','B.Tech IT',2024,5,5.6,3,'2024UIT3108','mohit.saxena.2024uit3108@nsut.ac.in');
INSERT INTO students VALUES('S1017','Aarav Das','B.Tech CSE',2023,7,6.51,0,'2023UCS2101','aarav.das.2023ucs2101@nsut.ac.in');
INSERT INTO students VALUES('S1018','Ishaan Taneja','B.Tech CSE',2023,7,6.8,1,'2023UCS2102','ishaan.taneja.2023ucs2102@nsut.ac.in');
INSERT INTO students VALUES('S1019','Vihaan Joshi','B.Tech CSE',2023,7,6.2,1,'2023UCS2103','vihaan.joshi.2023ucs2103@nsut.ac.in');
INSERT INTO students VALUES('S1020','Ritika Sinha','B.Tech CSE',2023,7,8.5,0,'2023UCS2104','ritika.sinha.2023ucs2104@nsut.ac.in');
INSERT INTO students VALUES('S1021','Aditya Gupta','B.Tech CSE',2023,7,7.5,1,'2023UCS2105','aditya.gupta.2023ucs2105@nsut.ac.in');
INSERT INTO students VALUES('S1022','Nikhil Walia','B.Tech CSE',2023,7,5.0,5,'2023UCS2106','nikhil.walia.2023ucs2106@nsut.ac.in');
INSERT INTO students VALUES('S1023','Pooja Mehta','B.Tech CSE',2023,7,6.84,0,'2023UCS2107','pooja.mehta.2023ucs2107@nsut.ac.in');
INSERT INTO students VALUES('S1024','Yash Sethi','B.Tech CSE',2023,7,7.48,0,'2023UCS2108','yash.sethi.2023ucs2108@nsut.ac.in');
INSERT INTO students VALUES('S1025','Pranav Sharma','B.Tech CSE',2024,5,8.0,0,'2024UCS2101','pranav.sharma.2024ucs2101@nsut.ac.in');
INSERT INTO students VALUES('S1026','Dhruv Verma','B.Tech CSE',2024,5,9.17,0,'2024UCS2102','dhruv.verma.2024ucs2102@nsut.ac.in');
INSERT INTO students VALUES('S1027','Harsh Khanna','B.Tech CSE',2024,5,8.51,0,'2024UCS2103','harsh.khanna.2024ucs2103@nsut.ac.in');
INSERT INTO students VALUES('S1028','Tushar Arora','B.Tech CSE',2024,5,6.5,1,'2024UCS2104','tushar.arora.2024ucs2104@nsut.ac.in');
INSERT INTO students VALUES('S1029','Ananya Grover','B.Tech CSE',2024,5,6.8,0,'2024UCS2105','ananya.grover.2024ucs2105@nsut.ac.in');
INSERT INTO students VALUES('S1030','Rahul Malhotra','B.Tech CSE',2024,5,8.61,0,'2024UCS2106','rahul.malhotra.2024ucs2106@nsut.ac.in');
INSERT INTO students VALUES('S1031','Reyansh Kapoor','B.Tech CSE',2024,5,8.72,0,'2024UCS2107','reyansh.kapoor.2024ucs2107@nsut.ac.in');
INSERT INTO students VALUES('S1032','Kritika Bose','B.Tech CSE',2024,5,5.4,3,'2024UCS2108','kritika.bose.2024ucs2108@nsut.ac.in');
CREATE TABLE courses (
    course_code TEXT PRIMARY KEY,           -- e.g. CS201
    course_name TEXT NOT NULL,
    programme   TEXT NOT NULL,              -- must match students.programme
    semester    INTEGER NOT NULL,
    credits     INTEGER NOT NULL,
    course_type TEXT                        -- extra: Theory / Lab / Theory+Lab
);
INSERT INTO courses VALUES('ITITC302','Database Management Systems','B.Tech IT',3,4,'Theory');
INSERT INTO courses VALUES('ITITC304','Advance Programming','B.Tech IT',3,4,'Theory');
INSERT INTO courses VALUES('ITITC501','Theory of Computation','B.Tech IT',5,4,'Theory');
INSERT INTO courses VALUES('ITITC503','Artificial Intelligence','B.Tech IT',5,4,'Theory');
INSERT INTO courses VALUES('ITITC504','Mobile Computing','B.Tech IT',5,4,'Theory');
INSERT INTO courses VALUES('COCSC302','Database Management Systems','B.Tech CSE',3,4,'Theory');
INSERT INTO courses VALUES('COCSC303','Design and Analysis of Algorithms','B.Tech CSE',3,4,'Theory');
INSERT INTO courses VALUES('COCSC501','Computer Networks','B.Tech CSE',5,4,'Theory');
INSERT INTO courses VALUES('COCSC503','Soft Computing','B.Tech CSE',5,4,'Theory');
INSERT INTO courses VALUES('COCSC504','Information and Data Security','B.Tech CSE',5,4,'Theory');
CREATE TABLE attendance (
    student_id       TEXT NOT NULL REFERENCES students(student_id),
    course_code      TEXT NOT NULL REFERENCES courses(course_code),
    classes_held     INTEGER NOT NULL,      -- > 0
    classes_attended INTEGER NOT NULL,      -- 0 <= attended <= held (% is computed by tools, never stored)
    PRIMARY KEY (student_id, course_code)
);
INSERT INTO attendance VALUES('S1002','ITITC501',40,30);
INSERT INTO attendance VALUES('S1003','ITITC503',40,29);
INSERT INTO attendance VALUES('S1004','ITITC504',40,24);
INSERT INTO attendance VALUES('S1004','ITITC503',40,26);
INSERT INTO attendance VALUES('S1009','ITITC501',40,30);
INSERT INTO attendance VALUES('S1009','ITITC503',37,35);
INSERT INTO attendance VALUES('S1009','ITITC504',42,35);
INSERT INTO attendance VALUES('S1010','ITITC501',43,39);
INSERT INTO attendance VALUES('S1010','ITITC503',40,29);
INSERT INTO attendance VALUES('S1010','ITITC504',41,33);
INSERT INTO attendance VALUES('S1011','ITITC501',37,33);
INSERT INTO attendance VALUES('S1011','ITITC503',44,41);
INSERT INTO attendance VALUES('S1011','ITITC504',40,24);
INSERT INTO attendance VALUES('S1012','ITITC501',41,24);
INSERT INTO attendance VALUES('S1012','ITITC503',38,34);
INSERT INTO attendance VALUES('S1012','ITITC504',43,34);
INSERT INTO attendance VALUES('S1013','ITITC501',37,34);
INSERT INTO attendance VALUES('S1013','ITITC503',38,32);
INSERT INTO attendance VALUES('S1013','ITITC504',42,40);
INSERT INTO attendance VALUES('S1014','ITITC501',44,39);
INSERT INTO attendance VALUES('S1014','ITITC503',37,33);
INSERT INTO attendance VALUES('S1014','ITITC504',38,33);
INSERT INTO attendance VALUES('S1015','ITITC501',36,32);
INSERT INTO attendance VALUES('S1015','ITITC503',43,36);
INSERT INTO attendance VALUES('S1015','ITITC504',37,33);
INSERT INTO attendance VALUES('S1016','ITITC501',44,38);
INSERT INTO attendance VALUES('S1016','ITITC503',43,41);
INSERT INTO attendance VALUES('S1016','ITITC504',39,33);
INSERT INTO attendance VALUES('S1018','COCSC501',40,30);
INSERT INTO attendance VALUES('S1019','COCSC503',40,27);
INSERT INTO attendance VALUES('S1021','COCSC504',36,27);
INSERT INTO attendance VALUES('S1022','COCSC501',40,31);
INSERT INTO attendance VALUES('S1022','COCSC503',40,20);
INSERT INTO attendance VALUES('S1022','COCSC504',40,33);
INSERT INTO attendance VALUES('S1025','COCSC501',40,30);
INSERT INTO attendance VALUES('S1025','COCSC503',43,35);
INSERT INTO attendance VALUES('S1025','COCSC504',44,40);
INSERT INTO attendance VALUES('S1026','COCSC501',42,40);
INSERT INTO attendance VALUES('S1026','COCSC503',40,29);
INSERT INTO attendance VALUES('S1026','COCSC504',39,37);
INSERT INTO attendance VALUES('S1027','COCSC501',44,37);
INSERT INTO attendance VALUES('S1027','COCSC503',39,35);
INSERT INTO attendance VALUES('S1027','COCSC504',40,24);
INSERT INTO attendance VALUES('S1028','COCSC501',39,36);
INSERT INTO attendance VALUES('S1028','COCSC503',37,30);
INSERT INTO attendance VALUES('S1028','COCSC504',38,36);
INSERT INTO attendance VALUES('S1029','COCSC501',43,35);
INSERT INTO attendance VALUES('S1029','COCSC503',43,40);
INSERT INTO attendance VALUES('S1029','COCSC504',37,35);
INSERT INTO attendance VALUES('S1030','COCSC501',37,34);
INSERT INTO attendance VALUES('S1030','COCSC503',37,30);
INSERT INTO attendance VALUES('S1030','COCSC504',43,41);
INSERT INTO attendance VALUES('S1031','COCSC501',40,36);
INSERT INTO attendance VALUES('S1031','COCSC503',44,36);
INSERT INTO attendance VALUES('S1031','COCSC504',37,35);
INSERT INTO attendance VALUES('S1032','COCSC501',37,32);
INSERT INTO attendance VALUES('S1032','COCSC503',44,40);
INSERT INTO attendance VALUES('S1032','COCSC504',38,34);
INSERT INTO attendance VALUES('S1001','ITITC501',45,35);
INSERT INTO attendance VALUES('S1001','ITITC503',42,39);
INSERT INTO attendance VALUES('S1001','ITITC504',41,37);
INSERT INTO attendance VALUES('S1002','ITITC503',41,35);
INSERT INTO attendance VALUES('S1002','ITITC504',38,30);
INSERT INTO attendance VALUES('S1003','ITITC501',41,32);
INSERT INTO attendance VALUES('S1003','ITITC504',42,36);
INSERT INTO attendance VALUES('S1004','ITITC501',44,37);
INSERT INTO attendance VALUES('S1005','ITITC501',41,32);
INSERT INTO attendance VALUES('S1005','ITITC503',40,34);
INSERT INTO attendance VALUES('S1005','ITITC504',41,32);
INSERT INTO attendance VALUES('S1006','ITITC501',45,35);
INSERT INTO attendance VALUES('S1006','ITITC503',39,35);
INSERT INTO attendance VALUES('S1006','ITITC504',39,31);
INSERT INTO attendance VALUES('S1007','ITITC501',42,33);
INSERT INTO attendance VALUES('S1007','ITITC503',45,36);
INSERT INTO attendance VALUES('S1007','ITITC504',43,35);
INSERT INTO attendance VALUES('S1008','ITITC501',45,35);
INSERT INTO attendance VALUES('S1008','ITITC503',41,36);
INSERT INTO attendance VALUES('S1008','ITITC504',39,31);
INSERT INTO attendance VALUES('S1009','ITITC302',38,36);
INSERT INTO attendance VALUES('S1009','ITITC304',45,41);
INSERT INTO attendance VALUES('S1010','ITITC302',40,31);
INSERT INTO attendance VALUES('S1010','ITITC304',43,38);
INSERT INTO attendance VALUES('S1011','ITITC302',43,38);
INSERT INTO attendance VALUES('S1011','ITITC304',42,34);
INSERT INTO attendance VALUES('S1012','ITITC302',40,35);
INSERT INTO attendance VALUES('S1012','ITITC304',40,35);
INSERT INTO attendance VALUES('S1013','ITITC302',38,30);
INSERT INTO attendance VALUES('S1013','ITITC304',39,33);
INSERT INTO attendance VALUES('S1014','ITITC302',39,33);
INSERT INTO attendance VALUES('S1014','ITITC304',41,35);
INSERT INTO attendance VALUES('S1015','ITITC302',40,37);
INSERT INTO attendance VALUES('S1015','ITITC304',39,30);
INSERT INTO attendance VALUES('S1016','ITITC302',39,35);
INSERT INTO attendance VALUES('S1016','ITITC304',39,33);
INSERT INTO attendance VALUES('S1017','COCSC501',41,36);
INSERT INTO attendance VALUES('S1017','COCSC503',39,34);
INSERT INTO attendance VALUES('S1017','COCSC504',39,33);
INSERT INTO attendance VALUES('S1018','COCSC503',40,31);
INSERT INTO attendance VALUES('S1018','COCSC504',44,34);
INSERT INTO attendance VALUES('S1019','COCSC501',39,33);
INSERT INTO attendance VALUES('S1019','COCSC504',45,40);
INSERT INTO attendance VALUES('S1020','COCSC501',44,35);
INSERT INTO attendance VALUES('S1020','COCSC503',45,36);
INSERT INTO attendance VALUES('S1020','COCSC504',39,33);
INSERT INTO attendance VALUES('S1021','COCSC501',45,40);
INSERT INTO attendance VALUES('S1021','COCSC503',43,33);
INSERT INTO attendance VALUES('S1023','COCSC501',42,38);
INSERT INTO attendance VALUES('S1023','COCSC503',39,31);
INSERT INTO attendance VALUES('S1023','COCSC504',39,34);
INSERT INTO attendance VALUES('S1024','COCSC501',39,36);
INSERT INTO attendance VALUES('S1024','COCSC503',44,40);
INSERT INTO attendance VALUES('S1024','COCSC504',42,37);
INSERT INTO attendance VALUES('S1025','COCSC302',45,38);
INSERT INTO attendance VALUES('S1025','COCSC303',45,43);
INSERT INTO attendance VALUES('S1026','COCSC302',45,35);
INSERT INTO attendance VALUES('S1026','COCSC303',45,35);
INSERT INTO attendance VALUES('S1027','COCSC302',40,35);
INSERT INTO attendance VALUES('S1027','COCSC303',44,37);
INSERT INTO attendance VALUES('S1028','COCSC302',39,35);
INSERT INTO attendance VALUES('S1028','COCSC303',40,33);
INSERT INTO attendance VALUES('S1029','COCSC302',44,41);
INSERT INTO attendance VALUES('S1029','COCSC303',44,34);
INSERT INTO attendance VALUES('S1030','COCSC302',42,36);
INSERT INTO attendance VALUES('S1030','COCSC303',45,39);
INSERT INTO attendance VALUES('S1031','COCSC302',41,36);
INSERT INTO attendance VALUES('S1031','COCSC303',39,34);
INSERT INTO attendance VALUES('S1032','COCSC302',40,34);
INSERT INTO attendance VALUES('S1032','COCSC303',39,36);
CREATE TABLE results (
    student_id     TEXT NOT NULL REFERENCES students(student_id),
    course_code    TEXT NOT NULL REFERENCES courses(course_code),
    exam_session   TEXT NOT NULL,           -- e.g. 2026-MAY
    exam_type      TEXT NOT NULL,           -- REGULAR or SUPPLEMENTARY
    internal_marks INTEGER,                 -- empty for ABSENT / DETAINED
    external_marks INTEGER,
    total_marks    INTEGER,                 -- = internal + external
    max_marks      INTEGER NOT NULL,        -- e.g. 100
    result         TEXT NOT NULL,           -- PASS, FAIL, ABSENT or DETAINED
    grade          TEXT,                    -- extra: letter grade (NSUT grading table)
    PRIMARY KEY (student_id, course_code, exam_session, exam_type)
);
INSERT INTO results VALUES('S1001','ITITC501','2025-DEC','REGULAR',39,37,76,100,'PASS','A');
INSERT INTO results VALUES('S1001','ITITC503','2025-DEC','REGULAR',31,23,54,100,'PASS','B');
INSERT INTO results VALUES('S1001','ITITC504','2025-DEC','REGULAR',39,44,83,100,'PASS','A+');
INSERT INTO results VALUES('S1002','ITITC501','2025-DEC','REGULAR',14,20,34,100,'FAIL','F');
INSERT INTO results VALUES('S1002','ITITC503','2025-DEC','REGULAR',29,38,67,100,'PASS','B+');
INSERT INTO results VALUES('S1002','ITITC504','2025-DEC','REGULAR',48,48,96,100,'PASS','O');
INSERT INTO results VALUES('S1003','ITITC501','2025-DEC','REGULAR',27,31,58,100,'PASS','B');
INSERT INTO results VALUES('S1003','ITITC503','2025-DEC','REGULAR',33,NULL,NULL,100,'ABSENT','Ab');
INSERT INTO results VALUES('S1003','ITITC504','2025-DEC','REGULAR',31,40,71,100,'PASS','B+');
INSERT INTO results VALUES('S1004','ITITC501','2025-DEC','REGULAR',18,15,33,100,'FAIL','F');
INSERT INTO results VALUES('S1004','ITITC503','2025-DEC','REGULAR',20,12,32,100,'FAIL','F');
INSERT INTO results VALUES('S1004','ITITC504','2025-DEC','REGULAR',34,NULL,NULL,100,'DETAINED','FD');
INSERT INTO results VALUES('S1005','ITITC501','2025-DEC','REGULAR',46,29,75,100,'PASS','A');
INSERT INTO results VALUES('S1005','ITITC503','2025-DEC','REGULAR',41,31,72,100,'PASS','A');
INSERT INTO results VALUES('S1005','ITITC504','2025-DEC','REGULAR',30,39,69,100,'PASS','B+');
INSERT INTO results VALUES('S1006','ITITC501','2025-DEC','REGULAR',41,14,55,100,'FAIL','F');
INSERT INTO results VALUES('S1006','ITITC501','2026-JUL','SUPPLEMENTARY',41,22,63,100,'PASS','B+');
INSERT INTO results VALUES('S1006','ITITC503','2025-DEC','REGULAR',40,40,80,100,'PASS','A');
INSERT INTO results VALUES('S1006','ITITC504','2025-DEC','REGULAR',44,47,91,100,'PASS','O');
INSERT INTO results VALUES('S1007','ITITC501','2025-DEC','REGULAR',40,27,67,100,'PASS','B+');
INSERT INTO results VALUES('S1007','ITITC503','2025-DEC','REGULAR',32,41,73,100,'PASS','A');
INSERT INTO results VALUES('S1007','ITITC504','2025-DEC','REGULAR',34,25,59,100,'PASS','B');
INSERT INTO results VALUES('S1008','ITITC501','2025-DEC','REGULAR',42,40,82,100,'PASS','A+');
INSERT INTO results VALUES('S1008','ITITC503','2025-DEC','REGULAR',28,35,63,100,'PASS','B+');
INSERT INTO results VALUES('S1008','ITITC504','2025-DEC','REGULAR',48,27,75,100,'PASS','A');
INSERT INTO results VALUES('S1009','ITITC302','2025-DEC','REGULAR',38,22,60,100,'PASS','B');
INSERT INTO results VALUES('S1009','ITITC304','2025-DEC','REGULAR',40,25,65,100,'PASS','B+');
INSERT INTO results VALUES('S1010','ITITC302','2025-DEC','REGULAR',33,39,72,100,'PASS','A');
INSERT INTO results VALUES('S1010','ITITC304','2025-DEC','REGULAR',28,35,63,100,'PASS','B+');
INSERT INTO results VALUES('S1011','ITITC302','2025-DEC','REGULAR',39,24,63,100,'PASS','B+');
INSERT INTO results VALUES('S1011','ITITC304','2025-DEC','REGULAR',32,36,68,100,'PASS','B+');
INSERT INTO results VALUES('S1012','ITITC302','2025-DEC','REGULAR',35,41,76,100,'PASS','A');
INSERT INTO results VALUES('S1012','ITITC304','2025-DEC','REGULAR',41,35,76,100,'PASS','A');
INSERT INTO results VALUES('S1013','ITITC302','2025-DEC','REGULAR',14,20,34,100,'FAIL','F');
INSERT INTO results VALUES('S1013','ITITC302','2026-JUL','SUPPLEMENTARY',30,35,65,100,'PASS','B+');
INSERT INTO results VALUES('S1013','ITITC304','2025-DEC','REGULAR',37,44,81,100,'PASS','A+');
INSERT INTO results VALUES('S1014','ITITC302','2025-DEC','REGULAR',26,30,56,100,'PASS','B');
INSERT INTO results VALUES('S1014','ITITC304','2025-DEC','REGULAR',35,NULL,NULL,100,'ABSENT','Ab');
INSERT INTO results VALUES('S1014','ITITC304','2026-JUL','SUPPLEMENTARY',32,NULL,NULL,100,'ABSENT','Ab');
INSERT INTO results VALUES('S1015','ITITC302','2025-DEC','REGULAR',28,27,55,100,'PASS','B');
INSERT INTO results VALUES('S1015','ITITC304','2025-DEC','REGULAR',39,33,72,100,'PASS','A');
INSERT INTO results VALUES('S1016','ITITC302','2025-DEC','REGULAR',10,10,20,100,'FAIL','F');
INSERT INTO results VALUES('S1016','ITITC304','2025-DEC','REGULAR',15,15,30,100,'FAIL','F');
INSERT INTO results VALUES('S1017','COCSC501','2025-DEC','REGULAR',48,39,87,100,'PASS','A+');
INSERT INTO results VALUES('S1017','COCSC503','2025-DEC','REGULAR',39,31,70,100,'PASS','B+');
INSERT INTO results VALUES('S1017','COCSC504','2025-DEC','REGULAR',28,35,63,100,'PASS','B+');
INSERT INTO results VALUES('S1018','COCSC501','2025-DEC','REGULAR',14,20,34,100,'FAIL','F');
INSERT INTO results VALUES('S1018','COCSC503','2025-DEC','REGULAR',48,27,75,100,'PASS','A');
INSERT INTO results VALUES('S1018','COCSC504','2025-DEC','REGULAR',34,38,72,100,'PASS','A');
INSERT INTO results VALUES('S1019','COCSC501','2025-DEC','REGULAR',30,29,59,100,'PASS','B');
INSERT INTO results VALUES('S1019','COCSC503','2025-DEC','REGULAR',25,NULL,NULL,100,'DETAINED','FD');
INSERT INTO results VALUES('S1019','COCSC504','2025-DEC','REGULAR',40,30,70,100,'PASS','B+');
INSERT INTO results VALUES('S1020','COCSC501','2025-DEC','REGULAR',33,40,73,100,'PASS','A');
INSERT INTO results VALUES('S1020','COCSC503','2025-DEC','REGULAR',33,35,68,100,'PASS','B+');
INSERT INTO results VALUES('S1020','COCSC504','2025-DEC','REGULAR',38,25,63,100,'PASS','B+');
INSERT INTO results VALUES('S1021','COCSC501','2025-DEC','REGULAR',29,42,71,100,'PASS','B+');
INSERT INTO results VALUES('S1021','COCSC503','2025-DEC','REGULAR',40,26,66,100,'PASS','B+');
INSERT INTO results VALUES('S1021','COCSC504','2025-DEC','REGULAR',20,10,30,100,'FAIL','F');
INSERT INTO results VALUES('S1022','COCSC501','2025-DEC','REGULAR',18,14,32,100,'FAIL','F');
INSERT INTO results VALUES('S1022','COCSC503','2025-DEC','REGULAR',20,NULL,NULL,100,'ABSENT','Ab');
INSERT INTO results VALUES('S1022','COCSC504','2025-DEC','REGULAR',22,11,33,100,'FAIL','F');
INSERT INTO results VALUES('S1023','COCSC501','2025-DEC','REGULAR',30,43,73,100,'PASS','A');
INSERT INTO results VALUES('S1023','COCSC503','2025-DEC','REGULAR',37,36,73,100,'PASS','A');
INSERT INTO results VALUES('S1023','COCSC504','2025-DEC','REGULAR',30,27,57,100,'PASS','B');
INSERT INTO results VALUES('S1024','COCSC501','2025-DEC','REGULAR',26,40,66,100,'PASS','B+');
INSERT INTO results VALUES('S1024','COCSC503','2025-DEC','REGULAR',32,29,61,100,'PASS','B');
INSERT INTO results VALUES('S1024','COCSC504','2025-DEC','REGULAR',27,25,52,100,'PASS','C');
INSERT INTO results VALUES('S1025','COCSC302','2025-DEC','REGULAR',45,35,80,100,'PASS','A');
INSERT INTO results VALUES('S1025','COCSC303','2025-DEC','REGULAR',33,29,62,100,'PASS','B');
INSERT INTO results VALUES('S1026','COCSC302','2025-DEC','REGULAR',37,42,79,100,'PASS','A');
INSERT INTO results VALUES('S1026','COCSC303','2025-DEC','REGULAR',37,28,65,100,'PASS','B+');
INSERT INTO results VALUES('S1027','COCSC302','2025-DEC','REGULAR',39,29,68,100,'PASS','B+');
INSERT INTO results VALUES('S1027','COCSC303','2025-DEC','REGULAR',32,22,54,100,'PASS','B');
INSERT INTO results VALUES('S1028','COCSC302','2025-DEC','REGULAR',14,20,34,100,'FAIL','F');
INSERT INTO results VALUES('S1028','COCSC302','2026-JUL','SUPPLEMENTARY',20,14,34,100,'FAIL','F');
INSERT INTO results VALUES('S1028','COCSC303','2025-DEC','REGULAR',33,31,64,100,'PASS','B+');
INSERT INTO results VALUES('S1029','COCSC302','2025-DEC','REGULAR',29,43,72,100,'PASS','A');
INSERT INTO results VALUES('S1029','COCSC303','2025-DEC','REGULAR',30,NULL,NULL,100,'ABSENT','Ab');
INSERT INTO results VALUES('S1029','COCSC303','2026-JUL','SUPPLEMENTARY',25,30,55,100,'PASS','B');
INSERT INTO results VALUES('S1030','COCSC302','2025-DEC','REGULAR',47,27,74,100,'PASS','A');
INSERT INTO results VALUES('S1030','COCSC303','2025-DEC','REGULAR',42,30,72,100,'PASS','A');
INSERT INTO results VALUES('S1031','COCSC302','2025-DEC','REGULAR',38,46,84,100,'PASS','A+');
INSERT INTO results VALUES('S1031','COCSC303','2025-DEC','REGULAR',45,25,70,100,'PASS','B+');
INSERT INTO results VALUES('S1032','COCSC302','2025-DEC','REGULAR',12,9,21,100,'FAIL','F');
INSERT INTO results VALUES('S1032','COCSC303','2025-DEC','REGULAR',13,11,24,100,'FAIL','F');
CREATE TABLE rule_registry (
    rule_id          TEXT PRIMARY KEY,      -- e.g. ATT-MIN-01
    description      TEXT NOT NULL,
    parameter        TEXT NOT NULL,         -- e.g. min_attendance_pct
    operator         TEXT NOT NULL,         -- >=, <=, in ...
    value            TEXT NOT NULL,         -- threshold value(s)
    scope_programmes TEXT NOT NULL DEFAULT 'ALL',
    scope_batches    TEXT NOT NULL DEFAULT 'ALL',
    effective_from   TEXT NOT NULL,         -- YYYY-MM-DD
    effective_to     TEXT DEFAULT '',       -- YYYY-MM-DD or empty
    source_doc_id    TEXT NOT NULL,         -- must exist in documents
    source_section   TEXT NOT NULL          -- clause, section or page
);
INSERT INTO rule_registry VALUES('ATT-MIN-01','Minimum attendance (lectures+tutorials+practicals, per subject) needed to appear in MSE/ESE','min_attendance_pct','>=','75','B.Tech','ALL','2019-07-01','','NSUT-BTECH-REG-2019','Cl. 11.2 (PDF p.18)');
INSERT INTO rule_registry VALUES('ATT-REL-01','Dean Academics may relax attendance by up to 10 percentage points on documented grounds','attendance_relaxation_pct','<=','10','B.Tech','ALL','2019-07-01','','NSUT-BTECH-REG-2019','Cl. 11.3 (PDF p.18)');
INSERT INTO rule_registry VALUES('ATT-REL-02','Further relaxation up to 5 percentage points in exceptional circumstances','attendance_extra_relaxation_pct','<=','5','B.Tech','ALL','2019-07-01','','NSUT-BTECH-REG-2019','Cl. 11.4 (PDF p.18)');
INSERT INTO rule_registry VALUES('ATT-REL-03','Maximum number of attendance relaxations in the whole programme','max_relaxations','<=','2','B.Tech','ALL','2019-07-01','','NSUT-BTECH-REG-2019','Cl. 11.5 (PDF p.18)');
INSERT INTO rule_registry VALUES('ATT-FLOOR-01','Not permitted to appear in MSE/ESE if attendance is below this value even after relaxation','attendance_floor_pct','>=','60','B.Tech','ALL','2019-07-01','','NSUT-BTECH-REG-2019','Cl. 11.6 (PDF p.18)');
INSERT INTO rule_registry VALUES('ATT-NOCONDONE-01','No shortage-of-attendance condonation at MSE; no relaxation claims at ESE; below 75% = detained from ESE','min_attendance_pct','>=','75','ALL','ALL','2026-09-15','','ACAD-ATT-2026','Para 1 (p.1, scanned)');
INSERT INTO rule_registry VALUES('PASS-ESE-01','Minimum share of ESE marks (theory and practical separately) to pass a course','min_ese_pct','>=','30','B.Tech','ALL','2019-07-01','','NSUT-BTECH-REG-2019','Cl. 12.7 (PDF p.19)');
INSERT INTO rule_registry VALUES('PASS-GRADE-D-01','Absolute grading (class size <= 30): minimum total marks for lowest passing grade D','min_total_marks_pct_for_D','>=','35','B.Tech','ALL','2019-07-01','','NSUT-BTECH-REG-2019','Table 5 (PDF p.15-16); Table 3 (p.14)');
INSERT INTO rule_registry VALUES('SUPP-01','No supplementary examinations; failed course must be re-registered (as amended by Exam-Only Mode / make-up exam circulars)','supplementary_allowed','=','false','B.Tech','ALL','2019-07-01','','NSUT-BTECH-REG-2019','Cl. 12.3 (PDF p.19)');
INSERT INTO rule_registry VALUES('PROMO-01','Promotion odd->even semester has no restriction','promotion_odd_to_even_restricted','=','false','B.Tech','ALL','2019-07-01','','NSUT-BTECH-REG-2019','Cl. 12.1');
INSERT INTO rule_registry VALUES('DEGREE-CREDITS-01','Credits to be earned for the B.Tech degree (out of 170 registered)','min_credits_degree','>=','162','B.Tech','ALL','2019-07-01','','NSUT-BTECH-REG-2019','Cl. 7.8 (PDF p.11); Cl. 15.1 (p.20)');
INSERT INTO rule_registry VALUES('DEGREE-CGPA-01','Minimum CGPA for award of B.Tech degree','min_cgpa_degree','>=','5.00','B.Tech','ALL','2019-07-01','','NSUT-BTECH-REG-2019','Cl. 15.1 (PDF p.20)');
INSERT INTO rule_registry VALUES('HONOURS-CGPA-01','Minimum CGPA for B.Tech (Honours)','min_cgpa_honours','>=','8.50','B.Tech','ALL','2019-07-01','','NSUT-BTECH-REG-2019','Cl. 7.9 / 15.4');
INSERT INTO rule_registry VALUES('DIV-FIRST-01','Minimum CGPA for First Division','min_cgpa_first_division','>=','6.50','B.Tech','ALL','2019-07-01','','NSUT-BTECH-REG-2019','Cl. 15');
INSERT INTO rule_registry VALUES('CGPA-PCT-01','Percentage of marks = CGPA multiplied by 10','cgpa_to_pct_multiplier','=','10','ALL','ALL','2019-07-01','','NSUT-BTECH-REG-2019','Cl. 9.7(d) (PDF p.17)');
INSERT INTO rule_registry VALUES('SUMMER-MAXCOURSES-01','Summer semester: max backlog/improvement courses (2026: 5 in total, at most 2 in Study Mode)','summer_max_courses','<=','5','ALL','ALL','2026-05-08','','DEAN-SUMMER-2026','Para on course limit (scanned)');
INSERT INTO rule_registry VALUES('SUMMER-ATT-01','Summer semester Study Mode: 75% attendance with no relaxation','min_attendance_pct','>=','75','ALL','ALL','2026-05-08','','DEAN-SUMMER-2026','Attendance clause (scanned)');
INSERT INTO rule_registry VALUES('REREG-FEE-01','Re-registration fee per subject in a regular semester (INR)','reregistration_fee_inr','=','7000','B.Tech','2026+','2026-05-14','','FEE-2026-27','Cl. 13 (scanned)');
INSERT INTO rule_registry VALUES('SUMMER-FEE-SM-01','Summer semester fee per paper, Study Mode (INR)','summer_fee_study_mode_inr','=','14000','ALL','ALL','2026-05-08','','DEAN-SUMMER-2026','Fee clause (scanned)');
INSERT INTO rule_registry VALUES('SUMMER-FEE-EOM-01','Summer semester fee per paper, Exam-Only Mode (INR)','summer_fee_eom_inr','=','10000','ALL','ALL','2026-05-08','','DEAN-SUMMER-2026','Fee clause (scanned)');
INSERT INTO rule_registry VALUES('PLACE-DROP-01','Final-year students may drop at most this many active backlogs for placement CGPA purposes','max_dropped_backlogs','<=','2','B.Tech','ALL','2024-07-01','2025-06-30','TNP-POLICY-2024-25','Drop Subject Rules (PDF p.11)');
INSERT INTO rule_registry VALUES('PLACE-CGPA-01','No university-wide minimum CGPA for placement; each company sets its own','univ_min_cgpa_placement','=','none','B.Tech','ALL','2024-07-01','2025-06-30','TNP-POLICY-2024-25','Eligibility (PDF p.4)');
COMMIT;
