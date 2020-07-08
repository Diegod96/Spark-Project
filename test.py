import mysql.connector as sql
from mysql.connector import Error
import dash
from dash.dependencies import Output, Input, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.express as px
import plotly.graph_objs as go
import sqlite3
import pandas as pd
from config import *

if __name__ == '__main__':
    app_colors = {
        'background': '#0C0F0A',
        'text': '#FFFFFF',
        'sentiment-plot': '#41EAD4',
        'volume-bar': '#FBFC74',
        'someothercolor': '#FF206E',
    }

    db_connection = sql.connect(host=database_endpoint_url, database=database_name, user=database_user,
                                password=database_password)

    cursor = db_connection.cursor(buffered=True)

    text = "trump"
    # cursor.execute("SELECT * FROM tweets WHERE text LIKE %s", ("%" + text + "%",))
    # record = cursor.fetchall()
    # print(record)

    query = "SELECT * FROM tweets WHERE text LIKE %s"
    df = pd.read_sql("SELECT * FROM tweets WHERE text LIKE %s", con=db_connection, params=("%" + text + "%",))
    print(df.head())





    sentiments = df['sentiment'].tolist()
    print(sentiments)

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

    values = [positive, negative, neutral]
    labels = ['Positive', 'Negative', 'Mixed']

    data = [go.Pie(
        labels=labels,
        values=values,
    )]

    fig = go.Figure(data=data)
    fig.update_traces(
        hoverinfo="text+value+percent",
        textinfo="label+percent",
        marker=dict(
            colors=['#fac1b7', '#a9bb95', '#92d8d8']
        ),
    )

    fig.show()
