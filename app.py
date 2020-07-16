import dash
import json
from dash.dependencies import Output, Input, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly
import os
import plotly.graph_objs as go
import sqlite3
import boto3
import pandas as pd
from config import *

conn = sqlite3.connect('twitter.db', check_same_thread=False)

app_colors = {
    'background': '#0C0F0A',
    'text': '#FFFFFF',
    'sentiment-plot': '#41EAD4',
    'volume-bar': '#FBFC74',
    'someothercolor': '#FF206E',
}

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                     html.Div(className='four columns div-user-controls',
                              children=[
                                  html.H2('Twitter Sentiment Dashboard'),
                                  html.P('Visualizing live twitter sentiment with Plotly - Dash.'),
                                  html.P(
                                      'Type a term in the search box below that you would like to see the sentiment from.'),
                                  html.Div(
                                      className='div-for-search',
                                      children=[
                                          dcc.Input(
                                              id='sentiment_term',
                                              placeholder='Enter a term...',
                                              type='text',
                                              value='',
                                              className='search'
                                          ),

                                      ],
                                      style={'color': ' #1E1E1E'})
                              ]
                              ),
                     html.Div(className='eight columns div-for-chars bg-black',
                              children=[
                                  dcc.Graph(id='live-graph', config={'displayModeBar': False}, animate=False),
                                  dcc.Interval(
                                      id='graph-update',
                                      interval=1 * 1000
                                  ),
                                  dcc.Graph(id='pie'),
                                  dcc.Interval(
                                      id='pie-update',
                                      interval=60 * 1000
                                  ),
                                  dcc.Graph(id='bar'),
                                  dcc.Interval(
                                      id='bar-update',
                                      interval=60 * 1000
                                  )

                              ])
                 ])
    ]
)


@app.callback(Output('live-graph', 'figure'),
              [Input(component_id='sentiment_term', component_property='value')],
              events=[Event('graph-update', 'interval')])
def update_graph_scatter(sentiment_term):
    """
    Find sentiment term in the SQLite DB and display it's sentiment live
    :param sentiment_term:
    :return:
    """
    try:
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 1000", conn,
                         params=('%' + sentiment_term + '%',))
        df.sort_values('unix', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df) / 5)).mean()

        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)

        df = df.resample('1000ms').mean()
        df.dropna(inplace=True)
        X = df.index
        Y = df.sentiment_smoothed

        data = plotly.graph_objs.Scatter(
            x=X,
            y=Y,
            name='Scatter',
            mode='lines+markers'
        )

        return {'data': [data], 'layout': go.Layout(xaxis=dict(range=[min(X), max(X)]),
                                                    yaxis=dict(range=[min(Y), max(Y)]),
                                                    colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400',
                                                              '#FF0056'],
                                                    template='plotly_dark',
                                                    paper_bgcolor='rgba(0, 0, 0, 0)',
                                                    plot_bgcolor='rgba(0, 0, 0, 0)',
                                                    margin={'b': 15},
                                                    hovermode='x',
                                                    autosize=True)}

    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')


def get_sentiment_data():
    global previous_data
    sqs = boto3.client('sqs', aws_access_key_id=accesskeyid,
                       aws_secret_access_key=secretaccesskey,
                       region_name=region)

    while True:
        resp = sqs.receive_message(
            QueueUrl=sentiment_queue_url,
            AttributeNames=['All'],
            MaxNumberOfMessages=1
        )

        try:
            data = []
            messages = resp['Messages']
            message = messages[0]
            string_body_dictionary = message['Body']
            body_dictionary = json.loads(string_body_dictionary)
            string_message_dictionary = body_dictionary.get('Message')
            sentiment_dictionary = json.loads(string_message_dictionary)
            positive = sentiment_dictionary.get('Positive')
            negative = sentiment_dictionary.get('Negative')
            neutral = sentiment_dictionary.get('Neutral')
            data.append(positive)
            data.append(negative)
            data.append(neutral)

            return data
        except KeyError:
            break


@app.callback(Output('pie', 'figure'),
              [Input(component_id='sentiment_term', component_property='value')],
              events=[Event('pie-update', 'interval')])
def update_pie(n):
    try:
        values = get_hashtag_data()
        labels = ['Positive', 'Negative', 'Mixed']
        print(labels, values)

        trace = go.Pie(labels=labels, values=values, title="Distribution of Twitter Sentiement",
                       hoverinfo='label+percent', textinfo='value',
                       textfont=dict(size=20, color=app_colors['text']),
                       marker=dict(
                           line=dict(color=app_colors['background'], width=2)))

        return {'data': [trace], 'layout': go.Layout(title="Distribution of Twitter Sentiement",
                                                     colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400',
                                                               '#FF0056'],
                                                     template='plotly_dark',
                                                     paper_bgcolor='rgba(0, 0, 0, 0)',
                                                     plot_bgcolor='rgba(0, 0, 0, 0)',
                                                     margin={'b': 15},
                                                     hovermode='x',
                                                     autosize=True)}


    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')


def get_hashtag_data():
    sqs = boto3.client('sqs', aws_access_key_id=accesskeyid,
                       aws_secret_access_key=secretaccesskey,
                       region_name=region)

    resp = sqs.receive_message(
        QueueUrl=hashtag_queue_url,
        AttributeNames=['All'],
        MaxNumberOfMessages=1
    )

    while True:

        try:
            messages = resp['Messages']
            message = messages[0]
            string_body_dictionary = message['Body']
            body_dictionary = json.loads(string_body_dictionary)
            string_message_dictionary = body_dictionary.get('Message')
            hashtag_dictionary = json.loads(string_message_dictionary)

            labels = []
            values = []

            for hashtag_labels in hashtag_dictionary:
                labels.append(hashtag_labels)

            for hashtag_values in hashtag_dictionary.values():
                values.append(hashtag_values)

            return labels, values

        except KeyError:
            break



@app.callback(Output('bar', 'figure'),
              [Input(component_id='sentiment_term', component_property='value')],
              events=[Event('bar-update', 'interval')])
def update_hash(n):
    try:
        labels, values = get_hashtag_data()
        print(labels, values)

        trace = go.Bar(x=labels, y=values)
        return {'data': [trace], 'layout': go.Layout(title="Distribution of Twitter Sentiement",
                                                     colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400',
                                                               '#FF0056'],
                                                     template='plotly_dark',
                                                     paper_bgcolor='rgba(0, 0, 0, 0)',
                                                     plot_bgcolor='rgba(0, 0, 0, 0)',
                                                     margin={'b': 15},
                                                     hovermode='x',
                                                     autosize=True)}

    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')




if __name__ == '__main__':
    app.run_server(debug=True)
