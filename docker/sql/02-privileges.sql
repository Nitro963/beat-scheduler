CREATE USER IF NOT EXISTS 'readonly_usr'@'%' IDENTIFIED BY 'readonly_password';
CREATE USER IF NOT EXISTS 'test_usr'@'%' IDENTIFIED BY 'test_password';

GRANT SELECT ON `%_db`.* TO 'readonly_usr'@'%';
GRANT ALL ON `test_db`.* TO 'test_usr'@'%';
FLUSH PRIVILEGES;