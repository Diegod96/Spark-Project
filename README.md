# Spark-Project
* Created a Twitter Dashbaord application that streams live twitter sentiment for the whole of twitter or for a specific user defined term (i.e. covid, biden, trump, etc.).
* There is a graph of live sentiment and a piechart of the distribution of sentiment for the current week.
* About 5 million tweets a day are being streamed and collected using Python, Tweepy API, and SQLite3 (TTL 24hrs).
* Same amount is being streamed and collected in longer term storage using AWS Kinesis Firehose, AWS S3, AWS RDS, Apache Spark/PySpark, and MySQL (TTL 7days).

## Code & Resources Used
**Python Version:** 3.8
**Databricks Runtime Version:** 6.5 (includes Apache Spark 2.4.5, Scala 2.11)
**Packages:** pandas, dash, plotly, vaderSentiment, boto3, tweepy, unidecode
**Full Requirements:** `pip install -r requirements.txt`
**PySpark Structured Streaming:** https://nycdatascience.com/blog/student-works/web-scraping/build-near-real-time-twitter-streaming-analytical-pipeline-scratch-using-spark-aws/
**Twitter Streamer via Tweepy:** https://pythonprogramming.net/twitter-stream-sentiment-analysis-python/
**Dash-Plotly:** https://www.statworx.com/de/blog/how-to-build-a-dashboard-in-python-plotly-dash-step-by-step-tutorial/

## Twitter Streamer
Tweaked the Twitter Streamer code above to only stream tweets that are in english. With each tweet we get alot of informtaion (id string, url to the tweet, name of user, etc.). What is useful for this project were the followuing:
* Timestamp of when the tweet was created (ts)
* The text of the tweet (text)
* The sentiment of the tweet after running the text through the sentiment analysis function (sentiment)

This data is then stored in a SQLite3 DB got the live sentiment graph, and streamed to an S3 Bucket via AWS Kinesis Firehose for the weekly sentient piechart.

## Spark Analysis
After streaming the data to S3, I need to analyze the data and package it in a way to be exported to my MySQL DB for longer term storage.
* Converted the PySpark Dataframe to a Pandas Dataframe to be able export to MySQL using the sqlalchemy library.
* Exported Dataframe to MySQL DB.

**TODO:**
* Do EDA on this data to get a look on how the data is comproised.
* Perform conversion of float value sentiment to overal sentiment (i.e. Positive, Neutral, and Negative) on ontebook rather than on the Dash - Plotly app.py to help with faster load times since I will not be querying from such a large DB table.

## Dash-Plotly
Now I have to display the data to the viewer. I used the Dash-Plotly articles code as framework since the style and layout fit the kind of look and style i was looking for.
The features that I implemented were the following:
* A search bar where the user can either leave it blank to see all of twitter's sentiement, or enter a term to see that term's sentiment
* A live graph with 1 and -1 (positive and negative) as the upper and lower bounds on the x-axis and the tweets timestamp on the y-axis
* A piechart that displays the sentiment of whatever term the user inputed in the serach bar for the current week
* Hosted on Heroku

**TODO:**
* Add more graphs and figures
* Reduce the amount of data that has to be queried to help with load times. I have noticed that the piechart takes a second or two to render.

## And Here Is The End Results
<img width="1919" alt="Dash" src="https://user-images.githubusercontent.com/25403763/87168178-161e6980-c29c-11ea-83f1-d3c1f45d0fd0.PNG">

**This Application Can Be Found At: https://diego-twitter-application.herokuapp.com/**



