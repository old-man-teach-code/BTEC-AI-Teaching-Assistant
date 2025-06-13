-- Initialize main database
CREATE DATABASE IF NOT EXISTS ai_assistant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the main database
USE ai_assistant;

-- Create system configuration table
CREATE TABLE IF NOT EXISTS system_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default configuration
INSERT INTO system_config (config_key, config_value) 
VALUES 
    ('system_version', '1.0.0'),
    ('app_server_type', 'main'),
    ('external_services_configured', 'false')
ON DUPLICATE KEY UPDATE 
    config_value = VALUES(config_value);

-- Create external services configuration table
CREATE TABLE IF NOT EXISTS external_services (
    id INT PRIMARY KEY AUTO_INCREMENT,
    service_name VARCHAR(100) UNIQUE NOT NULL,
    service_url VARCHAR(500),
    api_key VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    last_check TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default external services (to be configured)
INSERT INTO external_services (service_name, service_url, api_key, is_active) 
VALUES 
    ('n8n_server', NULL, NULL, false),
    ('ai_server', NULL, NULL, false)
ON DUPLICATE KEY UPDATE 
    service_name = VALUES(service_name);