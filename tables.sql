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

CREATE TABLE senate_annual_4b(
    report_url text,
    owner text, 
    ticker text, 
    ticker_url text, 
    asset_name text, 
    trans_type text, 
    trans_date date, 
    amount_min bigint, 
    amount_max bigint, 
    comment text)
    ;
ALTER TABLE senate_annual_4b
ADD CONSTRAINT senate_annual__4b_uniq UNIQUE (report_url, owner, ticker, ticker_url, asset_name, trans_type, trans_date, amount_min, amount_max, comment);

CREATE TABLE price(
    ticker text,
    date text, 
    vwap text)
    ;
ALTER TABLE price
ADD CONSTRAINT price_uniq UNIQUE (ticker, date, vwap);
