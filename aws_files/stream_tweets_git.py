from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
import json
import re
import boto3
import requests

# here we define the airline companies to analyse
authorized_mentions=['british_airways','americanair','united']
companies=['British_Airways','AmericanAir','united']

def get_mention(x):
	regex=re.compile('(@\w+)')
	m=regex.search(str(x))
	if m:
		return(m.group(1))
		
def remove_links(x):
	regex=re.compile('(.+)\shttp.+')
	m=regex.search(str(x))
	if m:
		return(m.group(1))
		
def clean_filter_sentiment(tweet):
	#first we want to remove the retweets, or the tweets containing too many entities:
	if ((tweet['retweeted']==True) or (len(tweet['entities']['user_mentions'])!=1)
		or ('RT' in tweet['text']) or (get_mention(tweet['text'])[1:].lower() not in authorized_mentions)):
		return (None)
	d={}
	# let's remove the links
	if 'http' in tweet['text']:
		d['text']={"S":remove_links(tweet['text'])}
	else:
		d['text']={"S":tweet['text']}
	#now we just return the fields we want
	d['created_at']={"S":tweet['created_at']}
	d['geo']={"S":str(tweet['coordinates'])}
	d['tweet_id']={"S":str(tweet['id'])}
	d['company']={"S":tweet['entities']['user_mentions'][0]['screen_name']}
	
	# then, if we have no text, we can't do anything
	# let's replace the company name by 'firm' and call the api to compute the sentiment of the tweet
	url='#############' # calling the api has a cost :)
	if ((d['text']['S'] is not None) & (get_mention(d['text']['S']) is not None)):
		d['text']['S']=d['text']['S'].replace(get_mention(d['text']['S']),'firm')
		payload={'text':d['text']['S']}
		r=requests.get(url,params=payload)
		d['sentiment']={"S":str(r.json()[0])}
		return(d)
	else:
		return (None)

    # now we call the topic classification api if the tweet is 	a complaint
	if d['sentiment']["S"]=="0":
		url='#############' # calling the api has a cost :)
		if ((d['text']['S'] is not None) & (get_mention(d['text']['S']) is not None)):
			d['text']['S']=d['text']['S'].replace(get_mention(d['text']['S']),'firm')
			payload={'text':d['text']['S']}
			r=requests.get(url,params=payload)
			d['sentiment']={"S":str(r.json()[0])}
			return(d)
		else:
			return (None)

class stream_twitter(Twitter):
	
	
	def __init__(self, company):

		CONSUMER_KEY='#######'
		CONSUMER_SECRET='#####'
		ACCESS_TOKEN='######'
		ACCESS_SECRET='#######'

		oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
		twitter = Twitter(auth=oauth)
		
		self.company = "@"+company
		self.raw_data = twitter.search.tweets(q=self.company, result_type='recent', lang='en', count=100)
		
	def get_valuable_tweets(self):
		l=[clean_filter_sentiment(self.raw_data['statuses'][i]) for i in range(len(self.raw_data['statuses']))]
		return ([s for s in l if s])


def lambda_handler(event,context):
	for firm in companies:
		raw_data=stream_twitter(firm)
		clean_data=raw_data.get_valuable_tweets()
		client = boto3.client('dynamodb')
		for d in clean_data:
			response = client.put_item(
					TableName='airline',
					Item=d)
		print(d)
	answer={'body':'ok','status':200}
	return(answer)