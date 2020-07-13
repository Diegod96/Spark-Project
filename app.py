import dash
from dash.dependencies import Output, Input, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import sqlite3
import pandas as pd
from config import database_name, database_password, database_endpoint_url, database_user

conn = sqlite3.connect('twitter.db', check_same_thread=False)
db_connection = sql.connect(host=database_endpoint_url, database=database_name, user=database_user,
                            password=database_password)

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
                                  dcc.Graph(id='live-graph', config={'displayModeBar': False}, animate=True),
                                  dcc.Interval(
                                      id='graph-update',
                                      interval=1 * 1000
                                  ),
                                  dcc.Graph(id='pie'),
                                  dcc.Interval(
                                      id='pie-update',
                                      interval=1 * 1000
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


@app.callback(Output('pie', 'figure'),
              [Input('sentiment_term', 'value'), Input('pie-update', 'interval')])
def update_pie(sentiment_term, _):
    try:

        db_connection = sql.connect(host=database_endpoint_url, database=database_name, user=database_user,
                                    password=database_password)
        cursor = db_connection.cursor(buffered=True)
        query = "SELECT * FROM tweets WHERE text LIKE %s"
        df = pd.read_sql("SELECT * FROM tweets WHERE text LIKE %s", con=db_connection,
                         params=("%" + sentiment_term + "%",))
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


        values = [positive, negative, neutral]
        labels = ['Positive', 'Negative', 'Mixed']
        # print(labels, values)

        trace = go.Pie(labels=labels, values=values, title="Distribution of Twitter Sentiement",
                       hoverinfo='label+percent', textinfo='value',
                       textfont=dict(size=20, color=app_colors['text']),
                       marker=dict(
                           line=dict(color=app_colors['background'], width=2)))

        return {'data': [trace], 'layout': go.Layout(title="Distribution of Twitter Sentiement",
                                                     # colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400',
                                                     #           '#FF0056'],
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
