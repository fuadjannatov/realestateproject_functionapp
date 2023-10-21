import pyodbc
import os
import dotenv
dotenv.load_dotenv()

from pkg_resources import run_script
import sys
import importlib.util
import logging
from datetime import datetime

logging.info('Opened DB_Connection.py file')

def runner_function(sn):
    sp = os.path.join(os.path.dirname(__file__), f'{sn}.py')

    s = importlib.util.spec_from_file_location(sn, sp)
    m = importlib.util.module_from_spec(s)
    sys.modules[s.name] = m
    s.loader.exec_module(m)

runner_function('Scraper')
#runner_function('Credentials')

from Scraper import ready_df

login = os.environ.get("login")
password = os.environ.get("password")
server = os.environ.get("server")
database = os.environ.get("database")

logging.info('Imported variables from Scraper.py')

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+login+';PWD='+ password)
cursor = cnxn.cursor()

params = list(tuple(row) for row in ready_df.head(ready_df.shape[0]).values)

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

query = 'INSERT INTO dbo.fulldb(AdNumber, Date, Type, Category, Floor, HighestFloor, Area, Rooms, Document, Mortgage, Renovation, Price, Lattitude, Longitude, District, NearbyPlaces, DateAdded) VALUES ({0})'    
query = query.format(','.join('?' * (len(ready_df.columns) + 1))) 



cursor.fast_executemany = True

def write_data(sql_query, parameters):
    
    length = len(parameters)
    logging.info(f'Started function write_data to write {length} datapoints')

    if len(parameters) > 1:
        for i in range(len(parameters)):
            addedAd = parameters[i][0]
            # cursor.execute(sql_query, parameters[i] + (timestamp,))
            # logging.info(f'Iterating through {length} datapoints to write to database. Wrote {addedAd}')
            try:
                cursor.execute(sql_query, parameters[i] + (timestamp,))
                logging.info(f'Iterating through {length} datapoints to write to database. Wrote {addedAd}')
            except:
                logging.info(f'{addedAd} was not written. Investigate')
                logging.info('Data writing did not succeed; > 1')
            
    elif len(parameters) == 1:
        addedAd = parameters[0][0]
        try:
            cursor.execute(sql_query, (parameters + (timestamp,)))
            logging.info(f'Successfully wrote 1 datapoint: {addedAd}')
        except:
            logging.info(f'{addedAd} was not written. Investigate')
            logging.info('Data writing did not succeed; == 1')

    else:
        logging.info(f'{addedAd} was not written. Investigate')
        logging.info('No data was writted.')

    return logging.info('write_data function has been executed successfully')

acquire = write_data(query, params)

cnxn.commit()
cursor.close()