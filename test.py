import mysql.connector as sql
import pandas as pd
import numpy as np
from config import *

if __name__ == '__main__':
    db_connection = sql.connect(host=database_endpoint_url, database=database_name, user=database_user,
                                password=database_password)
    db_cursor = db_connection.cursor()
    df = pd.read_sql("SELECT * FROM tweets WHERE text LIKE '%trump%' ", con=db_connection)

    sentiments = df['sentiment'].tolist()

    positive = 0
    neutral = 0
    negative = 0

    for sentiment in sentiments:
        sentiment = float(sentiment)
        if sentiment < -0.2:
            negative += 1
        if sentiment > 0.2:
            positive += 1
        else:
            neutral += 1

