import pypyodbc
import pandas as pd
from datetime import datetime

import config as cg


def connect_db(DATABASE_DIR, PWD):
    ''' connect to the database
    '''
    conn = None

    try:
        connection = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;PWD=%s'%(DATABASE_DIR,PWD)
        conn = pypyodbc.connect(connection)
        cursor =  conn.cursor()
    # print(f'connection : {connection}')
    # print(f'conn: {conn}')
    # print(f'cursor: {cursor}')
    except:
        return False, False
        print(f'>> cannot connect with the database. Bye~')

    return conn, cursor

def fetch_db(DATABASE_DIR, table, col, *,  PWD):
    ''' A function to pull out a column from  a table in the db
        DATABASE_DIR = database location
        table = name of the table
        column = name of the column'''

    conn, cursor = connect_db(DATABASE_DIR , PWD)

    if conn == False:
        col_lt = False
    else:
        col = cursor.execute(f'SELECT {col} FROM [{table}]')
        col = col.fetchall()
        col_lt = []
        for i in col:
            col_lt.append(list(i)[0])
        # Close the cursor and connection
        cursor.close()
        conn.close()

    return col_lt

def fetch_ndw(DATABASE_DIR, table_name, col, col_1,chno, col_2,  *,  PWD):
    ''' fetch the NDW factor closest to today
        DATABASE_DIR = database location
        table_name= name of the table
        col = output data
        col_1 = condition column 1
        chno = chamber number
        col_2 = condition column 2
        '''

    conn, cursor = connect_db(DATABASE_DIR , PWD)

    if conn == False:
        result = False
    else:

         sql = '''SELECT {col}
             FROM {table_name}
             WHERE {col_1} LIKE ? AND [{col_2}] = (SELECT MAX([{col_2}]) FROM {table_name} WHERE {col_1} LIKE ?);
          '''.format(col=col, table_name=table_name, col_1=col_1, col_2=col_2)



    # prepare values to substitute for ? in SQL
    params = (chno, chno)
    try:
        cursor.execute(sql, params)
        result = cursor.fetchone()
        result = result[0]
        print(f'results: {result, type(result)}')

        # Close the cursor and connection
        cursor.close()
        conn.close()

    except:
        result = 0 # if it is a new chamber, reture 0
        print(f'Fail to fetch NDW. You want to add this to the report')

    return result

def make_session_data(values):
    ''' make session data as a list
        session data = [Date/time(YYY-MM-DD HH:MM:SS),
                        operator_1(str),
                        operator_2(str),
                        Gantry (str),
                        Gantry angle (number),
                        ssChamber (str),
                        ssElectrometer (str),
                        ssElectrometer_range (str),
                        ssElectrometer_voltage (number),
                        fChamber (str),
                        fElectrometer (str),
                        fElectrometer_range (str),
                        fElectrometer_voltage (number),
                        ss_NDW (number),
                        f_NDW (number),
                        Material (str),
                        humidity (number),
                        comment (str) ]'''

    adate = datetime.strptime(values['-DATETIME-'], '%Y-%m-%d %H:%M:%S')


    session_entry = [adate, values['-PERSON1-'], values['-PERSON2-'], values['-GANTRY-'], int(values['-GA-']), \
                    values['-SSCH-'], values['-SS_ELE-'], values['-SS_ELE_RANGE-'], int(values['-SS_ELE_VOLT-']), \
                    values['-FCH-'], values['-F_ELE-'], values['-F_ELE_RANGE-'], int(values['-F_ELE_VOLT-']), \
                    float(values['-NDW-'])*1e9, float(values['-CALC-fNDW-'])*1e9, values['-MATERIAL-'], float(values['-HUMIDITY-']), \
                    values['-COMMENT-']]


    return session_entry

def push_session_data(DATABASE_DIR, session_data,  PWD = cg.PWD ):
    ''' DATABASE_DIR >> path_to_.accdb
        session_data >> a list [AData, MachineName,  Device, gantry angle, Operator1, Operator2, Comments]'''

    conn, cursor = connect_db(DATABASE_DIR , PWD = cg.PWD)

    sql = '''
          INSERT INTO RoosCalib_session VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          '''

    # try:
    cursor.execute(sql, session_data)
    conn.commit()
    return True
    # except:
    #     print(f' >> fail to push intercomparison session result to session table in the ASSESS database')
    #     return False

def make_measurement_data(values):
    ''' prepare the measurement data for database
        for each energy = [ADate(YYY-MM-DD HH:MM:SS),
                           Energy (number),
                           ssTemperature (Number),
                           ssPressure (Number),
                           ssR1 (number),
                           ssR2 (number),
                           ssR3 (number),
                           ssR4 (number),
                           ssR5 (number),
                           ssrTemperature (number),
                           ssrPressure (number),
                           ssrR6 (number),
                           ssrR7 (number),
                           ssrR8 (number),
                           fTemperature (number),
                           fPressure (number),
                           fR1 (number),
                           fR2 (number),
                           fR3 (number),
                           fR4 (number),
                           fR5 (number)

        ]
    '''
    adate = datetime.strptime(values['-DATETIME-'], '%Y-%m-%d %H:%M:%S')

    all_data = []
    '-ss_TEMP-'
    '-ss_PRESSURE-'
    tp = ['TEMP', 'PRESSURE']
    prefix = {'ss': 5, 'ssr': 3, 'f':5}

    for en in cg.pro_en:
        row = []
        row.append(adate)
        row.append(float(en))

        for p in list(prefix.keys()):
            for c in tp: # add temperature and pressure
                k = '-' + p + '_' + c + '-'
                row.append(float(values[k]))

            for i in range(1, prefix[p] + 1):
                k1 = '-' + p + 'R' + str(i) + '_' + en + '-'
                row.append(float(values[k1]))

        all_data.append(row)

    return all_data



def push_measurement_data(DATABASE_DIR, data, PWD = cg.PWD ):
    ''' DATABASE_DIR >> path_to_.accdb
        data >> a nested list. for each list: [ADate(YYY-MM-DD HH:MM:SS),
                                               Energy (number),
                                               ssTemperature (Number),
                                               ssPressure (Number),
                                               ssR1 (number),
                                               ssR2 (number),
                                               ssR3 (number),
                                               ssR4 (number),
                                               ssR5 (number),
                                               ssrTemperature (number),
                                               ssrPressure (number),
                                               ssrR6 (number),
                                               ssrR7 (number),
                                               ssrR8 (number),
                                               fTemperature (number),
                                               fPressure (number),
                                               fR1 (number),
                                               fR2 (number),
                                               fR3 (number),
                                               fR4 (number),
                                               fR5 (number)
        ]
        '''

    conn, cursor = connect_db(DATABASE_DIR, PWD = cg.PWD)

    sql = '''
          INSERT INTO RoosCalib_data VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

          '''

    try:

        for nr in data:

            cursor.execute(sql, nr)
            conn.commit()

            print(f'>> {nr[1]} MeV results are pushed to the database ')

        return True
    except:
        print(f' >> fail to push the {nr[1]} intercomparison results to spot data table in the ASSESS database')
        return False
