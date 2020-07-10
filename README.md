# Spark-Project
* Created a Twitter Dashbaord application that streams live twitter sentiment for the whole of twitter or for a specific user defined term (i.e. covid, biden, trump, etc.).
* There is a graph of live sentiment and a piechart of the distribution of sentiment for the current week.
* About 5 million tweets a day are being streamed and collected using Python, Tweepy API, and SQLite3 (TTL 24hrs).
* Same amount is being streamed and collected in longer term storage using AWS Kinesis Firehose, AWS S3, AWS RDS, Apache Spark/PySpark, and MySQL (TTL 7days).

## Code & Resources Used
* **Python Version:** 3.8
* **Databricks Runtime Version:** 6.5 (includes Apache Spark 2.4.5, Scala 2.11)
* **Packages:** pandas, dash, plotly, vaderSentiment, boto3, tweepy, unidecode
* **Full Requirements:** `pip install -r requirements.txt`
* **PySpark Structured Streaming:** https://nycdatascience.com/blog/student-works/web-scraping/build-near-real-time-twitter-streaming-analytical-pipeline-scratch-using-spark-aws/
* **Twitter Streamer via Tweepy:** https://pythonprogramming.net/twitter-stream-sentiment-analysis-python/

