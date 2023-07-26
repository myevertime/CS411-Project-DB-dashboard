CREATE OR REPLACE VIEW keywordView AS (
    SELECT id, name
    FROM keyword
    WHERE name in ('machine learning', 'artificial intelligence', 'computer vision', 'natural language processing')
);