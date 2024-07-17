import oracledb
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import os


def timeslot_extraction(connection):

    cursor = connection.cursor()

    sql_code = "SELECT * "
    sql_code += " FROM NSPTIMESLOTS "
    sql_code += " FETCH FIRST 200 ROWS ONLY"

    cursor.execute(sql_code)
    columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(cursor.fetchall(), columns = columns)

    return df


def timeslot_update(connection):
    cursor = connection.cursor()

    update_sql = """
    UPDATE nsp.opticket SET ACKNOWLEDGEDTIME = sysdate WHERE TICKETNO = '4177136724'
    """

    cursor.execute(update_sql)




if __name__ == '__main__':
    load_dotenv()
    user=os.getenv('USER_DSN')
    password=os.getenv('PASSWORD')
    dsn = os.getenv('DSN')

    connection = oracledb.connect(
    user= user,
    password= password,
    dsn= dsn)

    df=  timeslot_extraction(connection)

    print('check')
    print(df)