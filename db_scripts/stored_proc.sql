-- DROP PROCEDURE public.process_accounts_and_transaction_from_json(json);

CREATE OR REPLACE PROCEDURE public.process_accounts_and_transaction_from_json(IN p_json_data json, IN p_correlation_id uuid)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
    -- Generate a single UUID for all records in this batch insertion for traceability
    v_correlation_id uuid := p_correlation_id;
    v_client_id integer;
	v_process_type integer;
BEGIN
    -- 1. Extract the top-level client_id and process_type
    v_client_id := (p_json_data ->> 'client_id')::integer;
	v_process_type := (p_json_data ->> 'process_type')::integer;

    -- A record is considered valid if the 'field_validations' array is an empty JSON array '[]'.

	IF v_process_type = 1 THEN
		-- --- PROCESS TYPE 1: INSERT NEW ACCOUNT ---
	    WITH valid_fields AS (
	        -- Select only the valid records (where field_validations is empty)
	        SELECT
	            field ->> 'customer_name' AS customer_name,
	            field ->> 'customer_account' AS customer_account,
	            (field ->> 'balance_amount')::numeric(10, 2) AS balance_amount,
	            (field ->> 'amount_paid')::numeric(10, 2) AS transaction_amount
	        FROM
	            json_array_elements(p_json_data -> 'extracted_fields') AS field
	        WHERE
	            json_array_length(field -> 'field_validations') = 0
	    )
        INSERT INTO public.account (
            client_id, account_name, account_number, account_balance, account_fee_balance, correlation_id
        )
        SELECT
            v_client_id, vf.customer_name, vf.customer_account, vf.balance_amount, 0.00, v_correlation_id
        FROM valid_fields vf;

	ELSIF v_process_type = 2 THEN
		-- --- PROCESS TYPE 2: UPDATE ACCOUNT AND INSERT TRANSACTION (Payment) ---
	    WITH valid_fields AS (
	        -- Select valid records and get the account number and amount paid
	        SELECT
	            field ->> 'customer_account' AS account_number_match,
	            (field ->> 'amount_paid')::numeric(10, 2) AS transaction_amount
	        FROM
	            json_array_elements(p_json_data -> 'extracted_fields') AS field
	        WHERE
	            json_array_length(field -> 'field_validations') = 0
	    ),
	    updated_accounts AS (
	        -- UPDATE 1: Update the existing account balance
	        UPDATE public.account a
	        SET account_balance = a.account_balance - vf.transaction_amount -- Apply the payment (subtract amount_paid)
	        FROM valid_fields vf
	        WHERE
	            a.client_id = v_client_id
	            AND a.account_number = vf.account_number_match
	        RETURNING
	            a.id, a.account_name, vf.transaction_amount, v_correlation_id AS correlation_id
	    )
	    -- INSERT 2: Insert into the account_transaction table
	    INSERT INTO public.account_transaction (
	        account_id, transaction_amount, fee_amount, correlation_id
	    )
	    SELECT
	        ua.id,
	        ua.transaction_amount,
	        0.00,
	        ua.correlation_id
	    FROM updated_accounts ua;
        -- The final CTE's SELECT is implicitly executed for its DML (INSERT)

	END IF;
END;
$procedure$
;
