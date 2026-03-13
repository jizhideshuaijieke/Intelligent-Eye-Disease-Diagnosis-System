CREATE DATABASE IF NOT EXISTS eye_diagnosis_system_db
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE eye_diagnosis_system_db;

CREATE TABLE IF NOT EXISTS doctor (
    accountId INT PRIMARY KEY NOT NULL,
    name VARCHAR(50) DEFAULT NULL,
    gender VARCHAR(10) DEFAULT NULL,
    age INT DEFAULT NULL,
    department VARCHAR(50) DEFAULT NULL,
    photo MEDIUMTEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS Case_history (
    reportId VARCHAR(50) PRIMARY KEY NOT NULL,
    time VARCHAR(50) DEFAULT NULL,
    outcome VARCHAR(100) DEFAULT NULL,
    leftPhoto MEDIUMTEXT DEFAULT NULL,
    rightPhoto MEDIUMTEXT DEFAULT NULL,
    aiSuggestion MEDIUMTEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS patient (
    id INT PRIMARY KEY NOT NULL,
    name VARCHAR(50) DEFAULT NULL,
    gender VARCHAR(10) DEFAULT NULL,
    age INT DEFAULT NULL,
    reportId VARCHAR(50) NOT NULL UNIQUE,
    CONSTRAINT fk_patient_case_history
        FOREIGN KEY (reportId) REFERENCES Case_history(reportId)
);

CREATE TABLE IF NOT EXISTS Logging (
    accountId INT PRIMARY KEY NOT NULL,
    email VARCHAR(100) DEFAULT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    password MEDIUMTEXT DEFAULT NULL,
    CONSTRAINT fk_logging_doctor
        FOREIGN KEY (accountId) REFERENCES doctor(accountId)
);
