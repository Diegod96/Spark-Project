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


aws_key_id = os.environ.get("accesskeyid")
aws_key = os.environ.get("secretaccesskey")

conf = SparkConf().setAppName("first") 
sc = SparkContext.getOrCreate(conf=conf)
    
sc._jsc.hadoopConfiguration().set("fs.s3n.awsAccessKeyId",aws_key_id)
sc._jsc.hadoopConfiguration().set("fs.s3n.awsSecretAccessKey",aws_key)
config_dict = {"fs.s3n.awsAccessKeyId":aws_key_id,
               "fs.s3n.awsSecretAccessKey":aws_key}
bucket = "diego-twitter-stream-sink"
prefix = "/2020/07/*/*/*"
filename = "s3n://{}/{}".format(bucket, prefix)


rdd = sc.hadoopFile(filename,
                'org.apache.hadoop.mapred.TextInputFormat',
                'org.apache.hadoop.io.Text',
                'org.apache.hadoop.io.LongWritable',
                conf=config_dict)
spark = SparkSession.builder.appName("PythonWordCount").config("spark.files.overwrite","true").getOrCreate()

df = spark.read.json(rdd.map(lambda x: x[1]))
features_of_interest = ["ts", "text", "sentiment"]
df_reduce = df.select(features_of_interest)
# print(df_reduce.head())

url = "jdbc:mysql://database-1.cakatups2o7c.us-east-1.rds.amazonaws.com:3306/twitter"
table_name = "tweets"
mode_ = "overwrite"
password = os.environ.get("password")

df_reduce.write.format("jdbc").option("url", url)\
   .option("dbtable", table_name)\
   .option("driver", "com.mysql.jdbc.Driver")\
   .option("user", "admin")\
   .option("password", password)\
   .mode(mode_)\
   .save() 

print("Data saved to MySql Databaste")

# COMMAND ----------

