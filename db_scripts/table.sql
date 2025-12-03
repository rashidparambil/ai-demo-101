
-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Create the OLTP table for client detail
CREATE TABLE client (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create the Vector table for Rules
-- This is where the embedding lives, linked to the company
CREATE TABLE client_rule (
    id SERIAL PRIMARY KEY,
    client_id INT REFERENCES client(id) ON DELETE CASCADE,
    rule_content TEXT,             -- The actual text of the rule
    process_type int,              -- 1 - Placement 2 - Transaction
    embedding vector(3072)         -- The vector (size depends on model, e.g., Gemeni is 3072)
);

CREATE TABLE account (
    id SERIAL PRIMARY KEY,
    client_id INT REFERENCES client(id) ON DELETE CASCADE,
    account_name varchar(100),
	account_number varchar(50),
	account_balance decimal(10,2),
	account_fee_balance decimal(10,2),
	correlation_id uuid
);

CREATE TABLE account_transaction (
    id SERIAL PRIMARY KEY,
    account_id INT REFERENCES client(id) ON DELETE CASCADE,
    transaction_amount decimal(10,2),
	fee_amount decimal(10,2),
	correlation_id uuid
);

CREATE TABLE process_log (
    id SERIAL PRIMARY KEY,
    correlation_id uuid,
	process_type int, -- 1 - Placement 2 - Transaction
	error_detail text
);

CREATE TABLE table_details (
    id SERIAL PRIMARY KEY,
    table_description TEXT,             -- The actual text of the rule
    embedding vector(3072)         -- The vector (size depends on model, e.g., Gemeni is 768)
);
