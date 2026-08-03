CREATE DATABASE IF NOT EXISTS `student_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `student_db`;

CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(150) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `phone_number` VARCHAR(20) DEFAULT NULL,
    INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `students` (`student_name`, `email`, `password`, `phone_number`) VALUES
('Nguyen Van A', 'a.nguyen@gmail.com', '$2b$12$eImiTXuWVxfM37uY4JANjO...hash_password_1', '0901234567'),
('Tran Thi B', 'b.tran@gmail.com', '$2b$12$eImiTXuWVxfM37uY4JANjO...hash_password_2', '0987654321');