# Spark-Project
* Created a Twitter Dashboard application that streams live twitter sentiment for the whole of twitter or for a specific user defined term (i.e. covid, biden, trump, etc.).
* There is a graph of live sentiment and a piechart of the distribution of sentiment for the current week.
* About 5 million tweets a day are being streamed and collected using Python, Tweepy API, and SQLite3 (TTL 24hrs).
* The same amount of messages are being streamed to a Databricks notebook via AWS Kinesis Firehose.
* At the Databricks notebook, the data is being analyzed, formatted and loaded into a AWS SQS queue sitting in an AWS SNS topic.
* This notebook in running on a cron job for every minute, and the SQS queue is being purged every hour.
* This queue is being being polled by the dash-plotly frontend, specifically the piechart.


![Updating-Mozilla-Firefox-2020-08](https://user-images.githubusercontent.com/25403763/89300166-ca11db00-d635-11ea-9166-9f11ffe1d221.gif)


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
After streaming the data to S3, I need to analyze the data and package it in a way to be sent to a SQS queue in an SNS topic.
* Converted the PySpark Dataframe to a Pandas Dataframe to perform analysis on tweet sentiment.
* Packaged tweet sentiment into a dictionary.
* Exported dictionary to a SQS queue in an SNS topic.
* This notebok is running on a cron job every minute.


## Dash-Plotly
Now I have to display the data to the viewer. I used the Dash-Plotly articles code as framework since the style and layout fit the kind of look and style I was looking for.
The features that I implemented were the following:
* A search bar where the user can either leave it blank to see all of twitter's sentiement, or enter a term to see that term's sentiment
* A live graph with 1 and -1 (positive and negative) as the upper and lower bounds on the x-axis and the tweets timestamp on the y-axis
* A piechart that displays the sentiment of all of twitter. Updated every minute.
* About a 1:1 ratio of message being posted to the queue and the interval the messages are polled.

## KNOWN BUG
Whenever a user types in a term into the searchbar, the page is refreshed with every character. For example, if a user wants to search "baseball", the page will refresh on the user inputs of "b", "ba", "bas" ... until we get to "baseball". This is due to the database being queried on every charcter inputted in the search bar. This also means that the function that handles updating the piechart is also intitated on every refresh. Depending on the number of characters that are inputted, the piechart may display three pie squares of 1. This is due to messages being "in-flight" so it may take a couple of seconds for the messages to arrive to the piehcart be displayed. A fix on chnaging the way the database is queried is on the TODO.


## TODO
* ~~Reduce the amount of data that has to be queried on page load~~
* Chnage how database is queried to prevent page refresh on every character inputted to search bar.
* Do more EDA of the data in the Spark Analysis section
* Add more graphs and figures for the viewer
* Get trending hashtags



