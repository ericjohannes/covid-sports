
import tweepy
import pandas as pd
from json import load, dump
from os import path
import datetime

root = '..'
fn = 'secret.json'
secret_path = path.join(root, fn)
with open(secret_path, 'r') as f:
    secrets = load(f)


auth = tweepy.OAuthHandler(secrets['ApiKey'], secrets['ApiKeySecret'])
auth.set_access_token(secrets['AccessToken'], secrets['AccessTokenSecret'])

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

week_ago = datetime.datetime.now() - datetime.timedelta(days=10)

tweets = []

count = 1

# for tweet in tweepy.Cursor(api.search, q="@BNonnecke", count=450, since='2020-02-28').items(50000):
#
#     print(count)
#     count += 1
#
#     try:
#         data = [tweet.created_at, tweet.id, tweet.text, tweet.user._json['screen_name'], tweet.user._json['name'],
#                 tweet.user._json['created_at'], tweet.entities['urls']]
#         data = tuple(data)
#         tweets.append(data)
#
#     except tweepy.TweepError as e:
#         print(e.reason)
#         continue
#
#     except StopIteration:
#         break
# i'd like to look at every team's twitter and see when they announce cases, but
# a little research showed that the rockets didn't tweet about westbrook getting covid
# shams seems to tweet a lot about covid, so does the Athletic
# do an advanced search like (covid OR coronavirus OR COVID OR COVID-19) (from:JeffPassan)
userIDs = ['TheAthleticCFB',
           'TheAthleticNBA',
           'TheAthleticMLB',
           'TheAthleticNFL',
           'TheAthleticNHL',
           'ESPNCFB', # cfb
           'ESPNNBA',
           'ESPNNFL',
           'TSNHockey',  # nhl
           'sn_mlb', # sporting news mlb
           'AdamSchefter', # nfl
           'ShamsCharania', #nba
           'JeffPassan', # mlb
           'Brett_McMurphy', # cfb
           'TSNBobMcKenzie', # nhl

           # 'TheSteinLine',
           # 'WindhorstESPN',
           # 'wojespn'
            # 'cfb', # seems like it never tweets about covid
           ]

all_data = []
for u in userIDs:
    params = { 'screen_name':u,
               # 200 is the maximum allowed count
               'count':200,
               'include_rts' : False,
               'max_id' : None,
               # Necessary to keep full_text
               # otherwise only the first 140 words are extracted
               'tweet_mode' : 'extended'
    }

    oldest_id = False
    data = []
    reached_date = False
    while True:
        if len(data):
            params['max_id'] = data[-1]['tweet_id'] # - 1
        tweets = api.user_timeline(**params)
        if len(tweets) == 0: # got to end of tweets
            break

        for tweet in tweets:
            if tweet.created_at <= week_ago:
                reached_date = True
                break

            # simplify hashtags
            hashtags = []
            for ht in tweet.entities['hashtags']:
                hashtags.append(ht['text'])
            # hashtags = ','.join(hashtags)
            # , , , , ,
            onetweet = {'created_at': tweet.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                        'tweet_id': tweet.id,
                        'tweet_text': tweet.full_text,
                        'screen_name': tweet.user._json['screen_name'],
                        'hashtag': hashtags,
                        'covid_related': None,
                        }
            data.append(onetweet)
        if reached_date:
            break
    all_data.extend(data)


with open('test_tweets1.json', 'w') as json_file:
  dump(all_data, json_file)

# df = pd.DataFrame(all_data, columns = ['created_at','tweet_id', 'tweet_text', 'screen_name', 'hashtag',])
# df.to_json('test_tweets1.json',
#            orient='index'
#            # encoding='utf-8',
#            # index=False
#            )