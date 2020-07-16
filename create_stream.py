from tweepy import Stream, OAuthHandler
from tweepy.streaming import StreamListener
import json
import os
import boto3
import sqlite3
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from unidecode import unidecode
# from config import *

conn = sqlite3.connect('twitter.db', check_same_thread=False)
c = conn.cursor()

# Instantiate vaderSentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Credentials for Twitter & AWS
consumer_key = os.environ.get("ckey")
consumer_secret = os.environ.get("csecret")
access_token = os.environ.get("atoken")
access_token_secret = os.environ.get("atokensecret")
aws_key_id = os.environ.get("accesskeyid")
aws_key = os.environ.get("secretaccesskey")


def create_table():
    """
    Create SQLite Database for the live twitter sentiment line graph
    :return:
    """
    try:
        c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL)")
        c.execute("CREATE INDEX fast_unix ON sentiment(unix)")
        c.execute("CREATE INDEX fast_tweet ON sentiment(tweet)")
        c.execute("CREATE INDEX fast_sentiment ON sentiment(sentiment)")
        conn.commit()
    except Exception as e:
        print(str(e))


def sentiment_analysis(text):
    """
    Performs sentiment analysis on tweet text
    :param text:
    :return: sentiment
    """
    vs = analyzer.polarity_scores(text)
    sentiment = str(vs['compound'])
    return sentiment


def get_hashtag(all_data):
    """
    Parses the entities object of the tweepy json object and extracts the hashtag for a tweet
    If a tweet has no hastag then return an empty list
    Else, return the hashtag
    :param all_data:
    :return: hashtags
    """

    hashtag = ""
    entities = all_data.get('entities')
    hashtags_list = entities.get('hashtags')
    if not hashtags_list:
        return hashtag
    else:
        for hashtag_dictionary in hashtags_list:
            hashtag = unidecode(hashtag_dictionary.get('text'))
        return hashtag


class TweetStreamListener(StreamListener):

    def on_data(self, data):
        """
        Picks out english language tweets and parses them up into a dictionary of the tweet's timestamp, text,
        and sentiment score
        :param data:
        :return:
        """
        all_data = json.loads(data)
        tweet_data = {}
        try:
            if 'lang' in all_data and (all_data['lang'] == "en"):
                tweet_data['ts'] = str(all_data["timestamp_ms"])
                tweet_data['text'] = unidecode(all_data["text"])
                tweet_data['sentiment'] = str(sentiment_analysis(all_data["text"]))
                tweet_data['hashtag'] = get_hashtag(all_data)
                c.execute("INSERT INTO sentiment (unix, tweet, sentiment) VALUES (?, ?, ?)",
                          (tweet_data['ts'], tweet_data['text'], tweet_data['sentiment']))
                conn.commit()
                kinesis_client.put_record(
                    DeliveryStreamName=os.environ.get("stream_name_hashtags"),
                    Record={
                        'Data': json.dumps(tweet_data) + '\n'
                    }
                )
                kinesis_client.put_record(
                    DeliveryStreamName=os.environ.get("stream_name"),
                    Record={
                        'Data': json.dumps(tweet_data) + '\n'
                    }
                )
                print(tweet_data)


        except (AttributeError, KeyError, Exception) as e:
            print(e)
        return True

    def on_error(self, status):
        """
        Return an status code error
        :param status:
        :return:
        """
        print(status)


if __name__ == '__main__':
    create_table()
    kinesis_client = boto3.client('firehose',
                                  region_name=os.environ.get("region"),  # enter the region
                                  aws_access_key_id=os.environ.get("accesskeyid"),  # fill your AWS access key id
                                  aws_secret_access_key=os.environ.get("secretaccesskey"))  # fill you aws secret access key
    listener = TweetStreamListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, listener)
    stream.filter(track=["a", "e", "i", "o", "u"])
