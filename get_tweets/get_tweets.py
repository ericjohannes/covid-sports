
import tweepy
import pandas as pd
from json import load
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

week_ago = datetime.datetime.now() - datetime.timedelta(days=28)

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

userID = 'TheAthleticCFB'
oldest_id = False
params = { 'screen_name':userID,
           # 200 is the maximum allowed count
           'count':200,
           'include_rts' : False,
           'max_id' : None,
           # Necessary to keep full_text
           # otherwise only the first 140 words are extracted
           'tweet_mode' : 'extended'
}
data = []
reached_date = False
while True:
    if len(data):
        params['max_id'] = data[-1][1] # - 1
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
        hashtags = ','.join(hashtags)
        onetweet = [tweet.created_at,
                    tweet.id,
                    tweet.full_text,
                    tweet.user._json['screen_name'],
                    hashtags
                    ]
        data.append(tuple(onetweet))
    if reached_date:
        break
# tweets = api.user_timeline(screen_name=userID,
#                            # 200 is the maximum allowed count
#                            count=200,
#                            include_rts = False,
#                            # Necessary to keep full_text
#                            # otherwise only the first 140 words are extracted
#                            tweet_mode = 'extended'
#                            )

df = pd.DataFrame(data, columns = ['created_at','tweet_id', 'tweet_text', 'screen_name', 'hashtag',])
df.to_csv('test_tweets.csv')