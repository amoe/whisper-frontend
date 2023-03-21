CREATE TABLE item (
    pathname VARCHAR(1024) PRIMARY KEY,
    completed_date DATE,
    subtitles VARCHAR(131072)   -- 128k in bytes
);
