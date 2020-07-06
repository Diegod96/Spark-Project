import mysql.connector as sql
import pandas as pd
from config import database_name, database_password, database_endpoint_url, database_user


if __name__ == '__main__':
    db_connection = sql.connect(host=database_endpoint_url, database=database_name, user=database_user, password=database_password)
    db_cursor = db_connection.cursor()
    df = pd.read_sql("SELECT * FROM tweets WHERE text Like '%trump%'", con=db_connection)
    print(df.head())



