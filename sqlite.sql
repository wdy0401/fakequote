CREATE TABLE daily_price (
    date   INT,
    ctr    STRING,
    bdate  INT,
    edate  INT,
    close  DOUBLE,
    eclose DOUBLE,
    primary key (date,ctr,bdate))