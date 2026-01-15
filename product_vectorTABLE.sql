CREATE DATABASE IF NOT EXISTS product_search;
USE product_search;

CREATE TABLE products_vectors (
    product_id INT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    vector JSON NOT NULL,
    PRIMARY KEY (product_id),

    -- Optimizes prefix & typo searches
    FULLTEXT INDEX idx_product_name (product_name)
)
ENGINE=InnoDB;


//BLOB

ALTER TABLE products_vectors
MODIFY vector MEDIUMBLOB NOT NULL;