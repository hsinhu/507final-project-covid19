import sqlite3


DBNAME = 'covid19.sqlite'

def run_sql(query, data = None):
    '''Connect to database executes SQL query and return results.

    Parameters
    ----------
    query: string
        SQL string

    Returns
    -------
    list
        a list of tuples that represent the query result
    '''
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    if data is None:
        cur.execute(query)
        results = cur.fetchall()
        conn.close()
        return results
    else:
        cur.execute(query, data)
        conn.commit()
        conn.close()
        return


def insert_country_Cases(country_id, country_name, Confirmed,\
     Deaths, Recovered):
    insert_country_Cases = '''
        INSERT OR REPLACE INTO countryCases
        VALUES (?, ?, ?, ?, ?)
    '''
    data = [country_id, country_name, Confirmed,\
     Deaths, Recovered]
    run_sql(insert_country_Cases, data = data)
    return


def insert_state_Cases(state_name, case_num, case_per_100000_people,\
     death_num, death_per_100000_people):
    insert_state_Cases = '''
        INSERT OR REPLACE INTO stateCases
        VALUES (?, ?, ?, ?, ?)
    '''
    data = [state_name, case_num, case_per_100000_people,\
     death_num, death_per_100000_people]
    run_sql(insert_state_Cases, data = data)
    return


def insert_county_Cases(state_name, county_name, case_num, \
    case_per_100000_people, death_num, death_per_100000_people):
    insert_county_Cases = '''
        INSERT OR REPLACE INTO countyCases
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    data = [state_name, county_name, case_num, case_per_100000_people,\
     death_num, death_per_100000_people]
    run_sql(insert_county_Cases, data = data)
    return


def insert_Projection(State_Name, date_reported, allbed_mean, \
    ICUbed_mean, InvVen_mean, deaths_mean_daily, totalDeath_mean,\
        bedshortage_mean, icushortage_mean):

    insert_projection = '''
        INSERT OR REPLACE INTO stateProjection
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    data = [State_Name, date_reported, allbed_mean, \
    ICUbed_mean, InvVen_mean, deaths_mean_daily, totalDeath_mean,\
        bedshortage_mean, icushortage_mean]
    run_sql(insert_projection, data = data)
    return

if __name__ == "__main__":
    insert_state_Cases("New York", 242817, 1248, 13869, 71)