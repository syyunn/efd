CREATE TABLE [IF NOT EXISTS] senator (
    congress smallint,
    first_name text,
    last_name text,
    party text,
    url text,
);

ALTER TABLE senator
ADD CONSTRAINT senator_uniq UNIQUE (congress, first_name, last_name, party, url);


CREATE TABLE [IF NOT EXISTS] senate_annual (
   first_name text,
   last_name text,
   office text,
   report_type text,
   report_type_url text,
   date_received datetime
);
