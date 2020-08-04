# Databricks notebook source
from __future__ import print_function
import sys
import os
import re
from operator import add
import pandas as pd
from pyspark.sql.types import StructField, StructType, StringType
from pyspark.sql import Row
from pyspark.sql.types import *
from pyspark.sql import SQLContext
import json
import boto
import boto3
from boto.s3.key import Key
import boto.s3.connection
from pyspark.sql import SparkSession
from pyspark import SparkContext, SparkConf
from pyspark.ml.feature import MinMaxScaler
from pyspark.ml.linalg import Vectors, VectorUDT
from pyspark.sql.functions import *

# Get AWS credentials
aws_key_id = os.environ.get("accesskeyid")
aws_key = os.environ.get("secretaccesskey")

# Start spark instance
conf = SparkConf().setAppName("first") 
sc = SparkContext.getOrCreate(conf=conf)

# Allow spark to access my S3 bucket
sc._jsc.hadoopConfiguration().set("fs.s3n.awsAccessKeyId",aws_key_id)
sc._jsc.hadoopConfiguration().set("fs.s3n.awsSecretAccessKey",aws_key)
config_dict = {"fs.s3n.awsAccessKeyId":aws_key_id,
               "fs.s3n.awsSecretAccessKey":aws_key}
bucket = "diego-twitter-stream-sink"
prefix = "/2020/*/*/*/*"
filename = "s3n://{}/{}".format(bucket, prefix)

# Convert file from S3 bucket to an RDD
rdd = sc.hadoopFile(filename,
                'org.apache.hadoop.mapred.TextInputFormat',
                'org.apache.hadoop.io.Text',
                'org.apache.hadoop.io.LongWritable',
                conf=config_dict)
spark = SparkSession.builder.appName("PythonWordCount").config("spark.files.overwrite","true").getOrCreate()

# Map RDD to specific columns
df = spark.read.json(rdd.map(lambda x: x[1]))
features_of_interest = ["ts", "text", "sentiment", "hashtag"]
df_reduce = df.select(features_of_interest)

# COMMAND ----------

# Convert RDD to Pandas Dataframe
tweets_pdf = df_reduce.toPandas()

# Extract sentiments and hashtags
sentiments = tweets_pdf['sentiment'].tolist()
raw_hashtags = tweets_pdf['hashtag'].to_list()

# Get rid of blank hashtags
filter_object = filter(lambda x: x != '', raw_hashtags)
hashtags = list(filter_object)

# Tally top 10 hashtags
from collections import Counter 

Counter = Counter(hashtags)
most_occur = Counter.most_common(10) 

# Convert list of tuples to dictionary
def Convert(tup, di): 
    di = dict(tup) 
    return di 

dictionary = {}
hashtags_dictionary = Convert(most_occur, dictionary)

# Tally positive, negative, and neutral sentiment
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

# Put this sentiment in a dictionary 
values = [positive, negative, neutral]
values_dictionary = {"Positive":positive, "Negative":negative, "Neutral":neutral}

print(hashtags_dictionary)
print(values_dictionary)

# COMMAND ----------

# Send hashtag results to hashtag SNS topic
topicArn=os.environ.get("hashtagsnsnarn")
snsClient = boto3.client('sns', aws_access_key_id=aws_key_id, aws_secret_access_key=aws_key, region_name='us-east-1')
response = snsClient.publish(TopicArn=topicArn, Message=json.dumps(hashtags_dictionary), Subject='Hashtags', MessageAttributes = {"HashtagType": { "DataType": "String", "StringValue": "Count"}})
print(response['ResponseMetadata']['HTTPStatusCode'])


# Send sentiment results to sentiment SNS topic
topicArn=os.environ.get("SNSARN")
snsClient = boto3.client('sns', aws_access_key_id=aws_key_id, aws_secret_access_key=aws_key, region_name='us-east-1')
response = snsClient.publish(TopicArn=topicArn, Message=json.dumps(values_dictionary), Subject='Sentiment', MessageAttributes = {"SentimentType": { "DataType": "String", "StringValue": "SENTIMENT"}})
print(response['ResponseMetadata']['HTTPStatusCode'])

# COMMAND ----------

