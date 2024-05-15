CREATE DATABASE IF NOT EXISTS scanwise;
USE scanwise;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    passwd VARCHAR(255) NOT NULL,
    phone VARCHAR(12),
    role VARCHAR(20) NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

SELECT * FROM users;
truncate table users;

DELETE FROM users WHERE role != 'System Admin' AND id > 0;

#-------------------------------------------

CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL
);

select * from courses;

#-------------------------------------------------------


CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class VARCHAR(50) NOT NULL,
    year VARCHAR(50) NOT NULL,
    semester VARCHAR(50) NOT NULL,
    subjects TEXT NOT NULL,
    subject_codes TEXT NOT NULL
);

CREATE TABLE libbooks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class VARCHAR(50) NOT NULL,
    year VARCHAR(50) NOT NULL,
    semester VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    subject_codes VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    author VARCHAR(255) NOT NULL,
    publication VARCHAR(255) NOT NULL
  
);


select * from books;
#truncate table books;
#---------------------------------------------------------------------------


CREATE TABLE IF NOT EXISTS degreestudents (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name TEXT NOT NULL,
    class TEXT NOT NULL,
    prnnumber VARCHAR(20) NOT NULL UNIQUE,
    contact TEXT NOT NULL,
    address TEXT NOT NULL,
    dob DATE NOT NULL
     
);

select * from degreestudents;
SELECT COUNT(*) FROM degreestudents;
truncate table degreestudents;
