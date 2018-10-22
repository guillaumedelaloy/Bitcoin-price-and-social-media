from keras.models import model_from_json 
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
import pickle 
import json
import boto3

client = boto3.client('dynamodb')
s3 = boto3.resource('s3')
s3.Bucket('airline-twitter').download_file('topic_classif.json', '/tmp/topic_classif.json')
s3.Bucket('airline-twitter').download_file('topic_classif.h5', '/tmp/topic_classif.h5')
s3.Bucket('airline-twitter').download_file('tokenizer_topic_classif.pickle', '/tmp/tokenizer_topic_classif.pickle')

json_file = open('/tmp/topic_classif.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
loaded_model.load_weights("/tmp/topic_classif.h5")
print("Loaded model from disk")
with open("/tmp/tokenizer_topic_classif.pickle", "rb") as handle:
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