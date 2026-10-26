-- Database Schema for Web Laboratorium Peralatan Diagnostik


-- Table: users (Handles login for both admin via username and mahasiswa via nim)
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NULL,
    `nim` VARCHAR(30) UNIQUE NULL,
    `nama` VARCHAR(100) NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('admin', 'mahasiswa') NOT NULL DEFAULT 'mahasiswa',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: mahasiswa (Extended student info)
CREATE TABLE IF NOT EXISTS `mahasiswa` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `nim` VARCHAR(30) UNIQUE NOT NULL,
    `nama` VARCHAR(100) NOT NULL,
    `jurusan` VARCHAR(100) NOT NULL,
    `angkatan` VARCHAR(10) NOT NULL,
    `email` VARCHAR(100) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_mahasiswa_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: katalog (Item catalog)
CREATE TABLE IF NOT EXISTS `katalog` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `judul` VARCHAR(255) NOT NULL,
    `deskripsi` TEXT NOT NULL,
    `created_by` INT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_katalog_user` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: katalog_gambar (Images for catalog item, min 1 max 5, with thumbnail selector)
CREATE TABLE IF NOT EXISTS `katalog_gambar` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `katalog_id` INT NOT NULL,
    `file_path` VARCHAR(255) NOT NULL,
    `is_thumbnail` TINYINT(1) NOT NULL DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_gambar_katalog` FOREIGN KEY (`katalog_id`) REFERENCES `katalog` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
