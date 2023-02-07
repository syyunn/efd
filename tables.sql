CREATE TABLE [IF NOT EXISTS] senator (
    congress text,
    first_name text,
    last_name text,
    party text,
    url text,
);


CREATE TABLE [IF NOT EXISTS] senate_annual (
   first_name text,
   last_name text,
   office text,
   report_type text,
   report_type_url text,
   date_received datetime
);
