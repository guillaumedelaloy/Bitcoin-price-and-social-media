from keras.models import model_from_json 
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
import pickle 
import json
import boto3

client = boto3.client('dynamodb')
s3 = boto3.resource('s3')
s3.Bucket('airline-twitter').download_file('sentiment_airlines.json', '/tmp/sentiment_airlines.json')
s3.Bucket('airline-twitter').download_file('sentiment_airlines.h5', '/tmp/sentiment_airlines.h5')
s3.Bucket('airline-twitter').download_file('tokenizer_model_airlines.pickle', '/tmp/tokenizer_model_airlines.pickle')

json_file = open('/tmp/sentiment_airlines.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
loaded_model.load_weights("/tmp/sentiment_airlines.h5")
print("Loaded model from disk")
with open("/tmp/tokenizer_model_airlines.pickle", "rb") as handle:
    tokenizer=pickle.load(handle)
print(tokenizer)
max_words=35
def function(event, context): 
    tweets=event['queryStringParameters']['text']
    sentence=tweets.split(';;;')
    print(sentence)
    sentence=tokenizer.texts_to_sequences(sentence)
    sentence=sequence.pad_sequences(sentence, maxlen=max_words)
    pred=loaded_model.predict_classes(sentence)
    print(pred)
    answer={'body':str(pred),'statusCode':200}
    return(answer)