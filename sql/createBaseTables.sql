CREATE TABLE IF NOT EXISTS keywordView AS (
    SELECT id, name
    FROM keyword
    WHERE name in ('machine learning', 'artificial intelligence', 'computer vision', 'natural language processing')
);
CREATE TABLE IF NOT EXISTS facultyView AS (
    SELECT faculty_id, keyword_id, score
    FROM faculty_keyword
    WHERE keyword_id in (
        SELECT id
        FROM keywordView
    )
);
CREATE TABLE IF NOT EXISTS publicationView AS (
    SELECT publication_id, keyword_id, score
    FROM publication_keyword
    WHERE keyword_id in (
        SELECT id
        FROM keywordView
    )
);
CREATE TABLE IF NOT EXISTS univ_faculty AS (
    SELECT university_id, keyword_id, count(distinct id) as fac_cnt
    FROM (
        SELECT id, university_id
        from faculty
    ) AS faculty
    INNER JOIN (
        SELECT *
        FROM facultyView
    ) as facultyView
    ON faculty.id = facultyView.faculty_id
    GROUP BY university_id, keyword_id
);
CREATE TABLE IF NOT EXISTS univ_publication AS (
    SELECT university_id, keyword_id, count(distinct faculty_pub.publication_id) as pub_cnt
    FROM (
        SELECT id, university_id
        from faculty
    ) AS faculty
    INNER JOIN (
        SELECT *
        FROM faculty_publication
    ) as faculty_pub
    ON faculty.id = faculty_pub.faculty_id
    INNER JOIN (
        SELECT *
        FROM publicationView
    ) as publicationView
    ON faculty_pub.publication_id = publicationView.publication_id
    GROUP BY university_id, keyword_id
);
CREATE TABLE IF NOT EXISTS univ_krc AS (
    SELECT university_id, keyword_id, sum(KRC) as KRC
    FROM (
        SELECT faculty_id, keyword_id, sum(num_citations*score) as KRC
        FROM (
            SELECT *
            FROM faculty_publication
        ) as t1
        INNER JOIN (
            SELECT id, num_citations
            FROM publication
        ) as t2
        ON t1.publication_id = t2.id
        INNER JOIN (
            SELECT *
            FROM publicationView
        ) as t3
        ON t1.publication_id = t3.publication_id
        GROUP BY faculty_id, keyword_id
    ) as t
    INNER JOIN (
        SELECT id, university_id
        FROM faculty
    ) as meta2
    ON t.faculty_id = meta2.id
    GROUP BY university_id, keyword_id
);
CREATE TABLE IF NOT EXISTS keyword_univ_final AS (
    SELECT university_name, keyword_name, fac_cnt, pub_cnt, KRC
    FROM (
        SELECT university_id, keyword_id, fac_cnt
        FROM univ_faculty
    ) as t1
    INNER JOIN(
        SELECT university_id, keyword_id, pub_cnt
        FROM univ_publication
    ) as t2
    ON t1.university_id = t2.university_id AND t1.keyword_id = t2.keyword_id
    INNER JOIN(
        SELECT university_id, keyword_id, KRC
        FROM univ_krc
    ) as t3
    ON t1.university_id = t3.university_id AND t1.keyword_id = t3.keyword_id
    INNER JOIN(
        SELECT id, name as university_name
        FROM university
    ) as meta1
    ON t1.university_id = meta1.id
    INNER JOIN(
        SELECT id, name as keyword_name
        FROM keyword
    ) as meta2
    ON t1.keyword_id = meta2.id
);
CREATE TABLE IF NOT EXISTS univ_faculty_keyword AS (
    SELECT keywordview.faculty_id, university_id, publicationView.keyword_id, count(publicationView.publication_id) as pub_cnt, sum(num_citations*score) as KRC
    FROM (
        SELECT faculty_id, keyword_id
        FROM facultyView
    ) AS keywordview
    INNER JOIN (
        SELECT *
        FROM faculty_publication
    ) as pub
    ON keywordview.faculty_id = pub.faculty_id
    INNER JOIN (
        SELECT *
        FROM publicationView
    ) as publicationView
    ON publicationView.publication_id = pub.publication_id
    INNER JOIN (
            SELECT id, num_citations
            FROM publication
    ) as publication
    ON publication.id = publicationView.publication_id
    INNER JOIN (
        SELECT id, university_id
        from faculty
    ) as faculty
    ON keywordview.faculty_id = faculty.id
    GROUP BY faculty_id, university_id, keyword_id
);
CREATE TABLE IF NOT EXISTS keyword_faculty_final AS (
    SELECT fac_name, univ_name, keyword_name, pub_cnt, KRC
    FROM (
        SELECT *
        FROM univ_faculty_keyword
    ) AS t1
    INNER JOIN(
        SELECT id, name as univ_name
        FROM university
    ) AS t2
    ON t1.university_id = t2.id
    INNER JOIN(
        SELECT id, name as keyword_name
        FROM keywordView
    ) AS t3
    ON t1.keyword_id = t3.id
    INNER JOIN(
        SELECT id, name as fac_name
        FROM faculty
    ) AS t4
    ON t1.faculty_id = t4.id
);