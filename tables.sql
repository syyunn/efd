CREATE TABLE [IF NOT EXISTS] senator (
    congress smallint,
    first_name text,
    last_name text,
    party text,
    url text,
);

ALTER TABLE senator
ADD CONSTRAINT senator_uniq UNIQUE (congress, first_name, last_name, party, url);


CREATE TABLE senate_annual (
   url text,
   first_name text,
   last_name text,
   office text,
   report_type text,
   report_type_url text,
   date_received datetime
);

ALTER TABLE senate_annual
ADD CONSTRAINT senate_annual_uniq UNIQUE (url, first_name, last_name, office, report_type, report_type_url, date_received);