CREATE TABLE countryCases (
	Country_ID TEXT NOT NULL,
    Country_Name TEXT NOT NULL,
    Confirmed INTEGER,
    Deaths INTEGER,
    Recovered INTEGER,
    PRIMARY KEY(Country_ID)
);

CREATE TABLE stateCases (
    State_Name TEXT NOT NULL,
    Confirmed INTEGER,
    Confirmed_Per_100000_People NUMERIC,
    Deaths INTEGER,
    Deaths_Per_100000_People TEXT,
    PRIMARY KEY(State_Name)
);

CREATE TABLE countyCases (
	State_Name TEXT NOT NULL,
    County_name TEXT NOT NULL,
    Confirmed INTEGER,
    Confirmed_Per_100000_People NUMERIC,
    Deaths INTEGER,
    Deaths_Per_100000_People TEXT,
   
    FOREIGN KEY (State_Name) REFERENCES stateCases(State_Name) ON DELETE CASCADE,
    PRIMARY KEY(County_name, State_Name)
);


CREATE TABLE stateProjection (
    State_Name TEXT NOT NULL,
    date_reported DATE NOT NULL,
    allbed_mean NUMERIC,
    ICUbed_mean NUMERIC,
    InvVen_mean NUMERIC,
    deaths_mean_daily NUMERIC,
    totalDeath_mean NUMERIC,
    bedshortage_mean NUMERIC,
    icushortage_mean NUMERIC,
    PRIMARY KEY(State_Name, date_reported)
);


DELETE FROM countryCases;

DELETE FROM stateCases;
DELETE FROM countyCases;


DROP TABLE countryCases;

DROP TABLE stateCases;
DROP TABLE countyCases;

