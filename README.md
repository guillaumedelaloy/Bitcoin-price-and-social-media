# Introduction

Today, a good way get your flight reimbursed when facing a major problem is to publish your complaint social medias. I was curious about several things : 

Do people really use social medias to communicate with the airline companies ?
What are the most frequent complaints ?
Is there a significant difference in terms of customer experience between the companies (based on social media activity) ?

# Method

I have gathered during two weeks the tweets related to the biggest airline companies : American Air, United and British Airways. Thanks to this [data set](https://www.kaggle.com/crowdflower/twitter-airline-sentiment) found on Kaggle, I trained two models : 
- a sentiment classifier, in order to determine if the tweet is a complaint, a general remark, or a positive feed back from the customer
- a topic classification, in order to determine if a complaint is related to luggage issues, delays, cancellations...

In order to do this, I used the following AWS features:

- a lambda function called every 20 min in order to retrieve the tweets (I could have gone for 'every 3 min' but it is clearly too expensive and we would have retrieved many duplicated tweets)
- a lambda function computing the sentiment of a tweet, called through an API built with API Gateway
- a lambda function computing the topic of a complaints, called through an API built with API Gateway
- a S3 bucket storing the models trained locally



Here is a summary of the iterative process:


<p align="center">
  <img src= "https://github.com/guillaumedelaloy/airlines-complaints-microservice/blob/master/architecture.png?raw=true">
</p>


# Data cleaning

# Modeling

## Sentiment classifier

## Topic modeling

# Results

# Conclusions







