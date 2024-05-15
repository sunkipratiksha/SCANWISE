
CREATE DATABASE IF NOT EXISTS students;


USE students;

-- Create the degreestudents table
CREATE TABLE IF NOT EXISTS degreestudents (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name TEXT NOT NULL,
    class TEXT NOT NULL,
    prnnumber VARCHAR(20) NOT NULL UNIQUE,
    contact VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    dob DATE NOT NULL
     
);
select * FROM degreestudents;
truncate table degreestudents;
DROP table degreestudents;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    role ENUM('user', 'admin', 'superadmin') NOT NULL
);

select * FROM users;
truncate table users;
DROP table Users;
