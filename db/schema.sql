-- CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    label TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS thoughts (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    source_id INT REFERENCES sources(id),
    mood VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    label TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS thought_tags (
    thought_id INT REFERENCES thoughts(id),
    tag_id INT REFERENCES tags(id),
    PRIMARY KEY (thought_id, tag_id)
);

CREATE TABLE IF NOT EXISTS embeddings (
    thought_id INT PRIMARY KEY REFERENCES thoughts(id)
    -- vector VECTOR(384)
);

CREATE TABLE IF NOT EXISTS thought_links (
    id SERIAL PRIMARY KEY,
    from_id INT REFERENCES thoughts(id),
    to_id INT REFERENCES thoughts(id),
    type TEXT,
    score FLOAT
);
