CREATE DATABASE sales_management_system;
USE sales_management_system;
/**Create branches Table**/
CREATE TABLE branches (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    branch_admin_name VARCHAR(100) NOT NULL);
/**Create customer_sales Table**/
CREATE TABLE customer_sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT NOT NULL,
    sale_date DATE NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    mobile_number VARCHAR(15) UNIQUE NOT NULL,
    product_name VARCHAR(30) NOT NULL,
    gross_sales DECIMAL(12,2) NOT NULL,
    received_amount DECIMAL(12,2) DEFAULT 0.00,
    pending_amount DECIMAL(12,2)
        GENERATED ALWAYS AS (gross_sales - received_amount) STORED,
    status ENUM('Open','Close') DEFAULT 'Open',
	CONSTRAINT fk_customer_branch
    FOREIGN KEY (branch_id)
    REFERENCES branches(branch_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);
/**Create users Table**/
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    branch_id INT,
    role ENUM('Super Admin','Admin') NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,

    CONSTRAINT fk_user_branch
    FOREIGN KEY (branch_id)
    REFERENCES branches(branch_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE);
/**Create payment_splits Table**/
CREATE TABLE payment_splits (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    payment_date DATE NOT NULL,
    amount_paid DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,

    CONSTRAINT fk_payment_sale
    FOREIGN KEY (sale_id)
    REFERENCES customer_sales(sale_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE);
/**Create Trigger**/
DELIMITER $$
CREATE TRIGGER trg_after_payment_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales
    SET received_amount = (
        SELECT IFNULL(SUM(amount_paid),0)
        FROM payment_splits
        WHERE sale_id = NEW.sale_id)
    WHERE sale_id = NEW.sale_id;
	UPDATE customer_sales
    SET status = CASE
                    WHEN pending_amount = 0 THEN 'Close'
                    ELSE 'Open'
                 END
    WHERE sale_id = NEW.sale_id;
END$$
DELIMITER ;
/**Verify Tables**/
SHOW TABLES;
/**Check Trigger**/
SHOW TRIGGERS;
/**Delete all sample data and reset IDs**/
SET FOREIGN_KEY_CHECKS = 0;
/**truncate the tables**/
TRUNCATE TABLE branches;
TRUNCATE TABLE customer_sales;
TRUNCATE TABLE payment_splits;
TRUNCATE TABLE users;
/**enable foreign key checks**/
SET FOREIGN_KEY_CHECKS = 1;
/**verify that the trigger still exists**/
SHOW TRIGGERS;
















