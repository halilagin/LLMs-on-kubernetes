CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS document (
    id serial primary key,
    "text" text not null,
    source text not null,
    embedding vector(768)
);

SELECT count(*) FROM document;
