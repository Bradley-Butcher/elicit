CREATE TABLE IF NOT EXISTS document (
    document_id INTEGER PRIMARY KEY,
    document_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS extraction (
    extraction_id INTEGER PRIMARY KEY,
    method TEXT NOT NULL,
    confidence TEXT NOT NULL,
    exact_context TEXT,
    local_context TEXT,
    wider_context TEXT,
    validated_context TEXT,
    variable_id INTEGER,
    document_id INTEGER,
    valid TEXT DEFAULT NULL,
    CONSTRAINT fk_variable
        FOREIGN KEY (variable_id)
        REFERENCES variable(variable_id)
        ON DELETE CASCADE
    CONSTRAINT fk_document
        FOREIGN KEY (document_id)
        REFERENCES document(document_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS variable (
	variable_id INTEGER PRIMARY KEY,
	variable_name TEXT NOT NULL,
	variable_value TEXT NOT NULL,
    value_confidence TEXT,
    document_id INTEGER,
    CONSTRAINT fk_document
        FOREIGN KEY (document_id)
        REFERENCES document(document_id)
        ON DELETE CASCADE
);