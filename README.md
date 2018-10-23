# Introduction

Today, a good way get your flight reimbursed when facing a major problem is to share your complaint through social medias. I was curious about several things : 

1°) Do people really use social medias to communicate with the airline companies?
<br>
2°) What are the most frequent complaints?
<br>
3°) Which company should I choose if I want my flight to be on time?

# Method

I have gathered during two weeks the tweets mentioning  the following airline companies : American Air, United and British Airways. Thanks to this [data set](https://www.kaggle.com/crowdflower/twitter-airline-sentiment) found on Kaggle, I trained two models : 
- a sentiment classifier, in order to determine if the tweet is a complaint, a general remark, or a positive feed back from the customer
- a topic classification, in order to determine if a complaint is related to luggage issues, delays, cancellations...

In order to do this, I used the following AWS features (click on [lambda function](https://github.com/guillaumedelaloy/airlines-complaints-microservice/tree/master/aws_files) for the code):

- a [lambda function](https://github.com/guillaumedelaloy/airlines-complaints-microservice/blob/master/aws_files/stream_tweets_git.py) called every 20 min in order to retrieve the tweets (I could have gone for 'every 3 min' but it is clearly too expensive and we would have retrieved many duplicated tweets)
- a [lambda function](https://github.com/guillaumedelaloy/airlines-complaints-microservice/blob/master/aws_files/call_sentiment_git.py) computing the sentiment of a tweet, called through an API built with API Gateway
- a [lambda function](https://github.com/guillaumedelaloy/airlines-complaints-microservice/blob/master/aws_files/call_topic_classif_git.py) computing the topic of a complaints, called through an API built with API Gateway
- a S3 bucket storing the models trained locally

If you have any question related to connecting lambdas to S3 buckets or API gateway, feel free to contact me :) !



Here is a summary of the iterative process:


<p align="center">
  <img src= "https://github.com/guillaumedelaloy/airlines-complaints-microservice/blob/master/image/architecture.png?raw=true">
</p>


# Data cleaning

Let's have a look at what the raw tweets look like:

```
1: @JetBlue I'll pass along the advice. You guys rock!!
2: @united I sent you a dm with my file reference number.. I just want to know if someone has locat...
3: @SouthwestAir Black History Commercial is really sweet. Well done.
4: @SouthwestAir why am I still in Baltimore?! @delta is doing laps around us and laughing about it...
5: @SouthwestAir SEA to DEN. South Sound Volleyball team on its way! http://t.co/tN5cXCld6M

```
We should make the following transformations:
- t1 : remove the urls starting with http -> regex
- t2 : we assume that when two companies are mentioned, as in tweet 4, it is very complex to understand which company the customer is talking to -> we will keep only the tweets with one company mentioned
 
 We can also use wordcloud to map the most frequent words:
 
 <p align="center">
  <img src= "https://github.com/guillaumedelaloy/airlines-complaints-microservice/blob/master/image/wordcloud_airline_1.png?raw=true">
</p>

We don't want the models to learn on specific companies names:
- t3 : replace company name by 'firm'

The new sample and the new cloud of words with the clean data looks like:

```
1: @firm I'll pass along the advice. You guys rock!!
2: @firm I sent you a dm with my file reference number.. I just want to know if someone has locat...
3: @firm Black History Commercial is really sweet. Well done.
4: 
5: @firm SEA to DEN. South Sound Volleyball team on its way!

```

 <p align="center">
  <img src= "https://github.com/guillaumedelaloy/airlines-complaints-microservice/blob/master/image/wordcloud_airline_2.png?raw=true">
</p>

We will apply those transformations to both the training dataset and the data collected and stored in the dynamo table.

Code for cleaning data/training the models is available [here](airlines-complaints-microservice/airlines_complaints_analysis.ipynb)

# Modeling

Our training dataset has initially 14640 lines with the following features:
tweet_id, text of the tweet, date, sentiment (0 for negative, 1 for neutral, 2 for positive), negativereason,

where the possible negative reasons are:

```
'Bad Flight', "Can't Tell", 'Late Flight',
       'Customer Service Issue', 'Flight Booking Problems', 'Lost Luggage',
       'Flight Attendant Complaints', 'Cancelled Flight',
       'Damaged Luggage', 'longlines'
```
For both model: 
- we will rebalance the classes by artificially upsampling the training set
- we will use Keras (Tensorflow as backend) to design a neural network
- we transform the tweets into vectors of size (num_words=35, voc_size=10000) by a bag of words technique
- the architecture of the nn is : one embedding layer (35, embedding dim=100), one LSTM layer(1,100), one Dense layer (1,size = number of classes)


## Sentiment classifier

We obtain a final accuracy of : 92.36 %

<p align="center">
  <img src= "https://github.com/guillaumedelaloy/airlines-complaints-microservice/blob/master/image/sentiment_training.png?raw=true">
</p>

## Topic modeling

I rearranged a bit the categories of neagtive reasons because the category ```Bad flight``` was quite blurry and hard to differenciate. As a consequence, I merged the category with ```Can't Tell```, which means it is not clear to identify the main reason of the complaint.

We obtain a final accuracy of : 97.68 %

<p align="center">
  <img src= "https://github.com/guillaumedelaloy/airlines-complaints-microservice/blob/master/image/topic_training.png?raw=true">
</p>

# Results and Interpretations

Here is the distribution of the counts of complaints between the 3 companies we selected:
<br>
<p align="center">
  <img src= "https://github.com/guillaumedelaloy/airlines-complaints-microservice/blob/master/image/distrib_complaints.png?raw=true">
</p>
<br>
<br>
Here we normalize the distribution with the total number of complaints of each company:
<br>
<p align="center">
  <img src= "https://github.com/guillaumedelaloy/airlines-complaints-microservice/blob/master/image/topic_rep.png?raw=true">
</p>
It is time now to answer the three questions of the introduction:

1°) People do use social media to interact with the company : about 90K mentions per day for AmericanAir (6700 flights per day)
<br>
2°) Rankings of the frequencies of complaints are the same in each company, and follow this order (from the most frequent to the least common):

<br>
```
1st - Customer Service Issue
2nd - Late Flight
3rd - Luggage
5th - Flight Booking Problems & Flight Attendant Complaints
6th - Cancelled Flight
7th - Long Lines
```

However, the probabilites of the type of complaints are not the same between the companies.
Kruskall Wallis test results: ```KruskalResult(statistic=20.93635239906925, pvalue=2.8426856747332026e-05)```
We strongly reject the hypothesis of equal probabilities of the complaints between the companies.
 

<br>
3°) Let's conduct a two sample t-test in order to check if there is a significant difference between p_united=P(complaint='Late Flight', company='united') and p_brit=P(complaint='Late Flight', company='bristish_airways').
```

H0 : p_united-p_brit=0
H1 : p_united-p_brit!=0

With X being the number of late flight complaint and N the total number of complaints:
X_brit=381 , N_brit=2273
X_united=787, N_united=2787

Then we have : 


p_pooled^=(X_brit+X_united)/(N_brit+N_united)=0.233

SE=[(p*(1-p)*(1/N_brit + 1/N-united)]^0.5=0.012

d^=(X_united/N_united) - (X_brit/N_brit)=0.1183

confidence interval= d^ +/- 1.96*SE , for alpha=0.05
CI=[0.095;0.14]

CI does not include 0, so we can conclude that the difference of frequencies of 
complaints related to delayed flights didn't occur by chance with a confidence of 95%!
```

As a consequence, we should choose British airways in order to avoid delays! (*)


*obviously, we can't really say so because the study is only based on a sample of tweets that do not reflect the whole flight traffic of those companies. Moreover, as British and United do not operate on the same areas, and considering that the period of study is rather small (2 weeks), an external event such as a storm in the US could cause way more delays for United than British Airways.








