/* Create Index on keyword_univ_final table */
CREATE INDEX idx_university_name ON keyword_univ_final (university_name);

/* Create Trigger to make length constraint on keyword name column */
ALTER TABLE keyword ADD COLUMN word_count INT;

DELIMITER $$
CREATE TRIGGER update_word_count
BEFORE INSERT ON keyword
FOR EACH ROW
BEGIN
  SET NEW.word_count = LENGTH(NEW.name);
END $$
DELIMITER ;

ALTER TABLE keyword
ADD CONSTRAINT check_word_count
CHECK (word_count > 2);