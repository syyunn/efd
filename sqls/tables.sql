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

CREATE TABLE senate_annual_4a(
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
ALTER TABLE senate_annual_4a
ADD CONSTRAINT senate_annual__4a_uniq UNIQUE (report_url, owner, ticker, ticker_url, asset_name, trans_type, trans_date, amount_min, amount_max, comment);



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
    date date, 
    vwap float)
    ;
ALTER TABLE price
ADD CONSTRAINT price_uniq UNIQUE (ticker, date, vwap);


CREATE TABLE _sandbox_suyeol.ticker_naics_url (
    ticker text,
    asset_name text,
    naics_url text
)

ALTER TABLE _sandbox_suyeol.ticker_naics_url
ADD CONSTRAINT _sandbox_suyeol_ticker_naics_url UNIQUE (ticker, asset_name, naics_url);

CREATE TABLE _sandbox_suyeol.ticker_naics (
    naics_url text,
    duns text,
    company_name text, 
    trade_style text,
    url text, 
    naics1 text, 
    naics1_desc text,  
    naics2 text,
    naics2_desc text, 
    sic1 text, 
    sic1_desc text, 
    sic2 text, 
    sic2_desc text, 
    total_emp int, 
    sales_volume bigint
);

ALTER TABLE _sandbox_suyeol.ticker_naics
ADD CONSTRAINT _sandbox_suyeol_ticker_naics UNIQUE (naics_url);


CREATE TABLE _sandbox_suyeol.ticker_naics_zoom (
    ticker text,
    asset_name text,
    naics text,
);

ALTER TABLE _sandbox_suyeol.ticker_naics_zoom
ADD CONSTRAINT ticker_naics_zoom UNIQUE (ticker);