CREATE TABLE IF NOT EXISTS restaraunts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `location` TEXT,
    reviews VARCHAR(255),
    rating VARCHAR(255),
    `name` VARCHAR(255),
    email VARCHAR(255),
    pos_in_rate VARCHAR(255),
    `number` VARCHAR(255),
    prices VARCHAR(1000),
    food_rating VARCHAR(255),
    service_rating VARCHAR(255),
    value_rating VARCHAR(255),
    atmosphere_rating VARCHAR(255),
    g_code VARCHAR(255),
    city VARCHAR(255),
    link VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
