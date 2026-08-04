CREATE DATABASE IF NOT EXISTS `student_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `student_db`;

CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_code` VARCHAR(50) NOT NULL UNIQUE,
    `student_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(150) NOT NULL UNIQUE,
    `password` VARCHAR(255) DEFAULT NULL,
    `phone_number` VARCHAR(20) DEFAULT NULL,
    `age` INT DEFAULT NULL,
    `is_active` TINYINT(1) DEFAULT 1,
    INDEX `idx_student_code` (`student_code`),
    INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `students` (`student_code`, `student_name`, `email`, `password`, `phone_number`, `age`, `is_active`) VALUES
('SV001', 'Nguyen Van A', 'a.nguyen@gmail.com', '123456', '0901234567', 20, 1),
('SV002', 'Tran Thi B', 'b.tran@gmail.com', '123456', '0987654321', 22, 1);
