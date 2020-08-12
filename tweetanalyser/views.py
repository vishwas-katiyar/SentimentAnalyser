### Import Dependencies and packages

from django.shortcuts import render
from django.http import HttpResponse
import tweepy
from textblob import TextBlob
from collections import Counter
import pandas as pd 
import numpy as np 
import re
import nltk
from nltk.stem.porter import *
from nltk.stem import WordNetLemmatizer 

### Setting up Keys

Consumer_Key ="ILExflCl7VbbErhgQ92KhFSrv"
Consumer_Token_Secret ="DDnjdU2OCZjrrrTAMcU3ieiIQPxg8u2Gv59aTNhc4IAcB3nEzD"
Access_Token="1043195580804026368-mUXL4J2Ng5ytxTViHon2FEfEizYTv1"
Access_Token_Secret="pNS5StYBcyTSsWgkcIuCY7idv5LG0ny83AKP7B17AdtYy"
auth = tweepy.OAuthHandler(Consumer_Key, Consumer_Token_Secret)
auth.set_access_token(Access_Token, Access_Token_Secret)
api = tweepy.API(auth, wait_on_rate_limit=True)
 
### Object initiallization for tokenization and stemming

w_tokenizer = nltk.tokenize.WhitespaceTokenizer()
lemmatizer = nltk.stem.WordNetLemmatizer()
stemmer = PorterStemmer()
    
### Method for landing page

def home(request):
        
    return render(request,'index.html')

### Method for fetching tweets

def fetch_tweet(sc_name):
    
    postt=api.user_timeline(screen_name = sc_name, count =1000, lang ="en", tweet_mode = "extended",include_rts=False)
        
    return postt

### Method for Data Cleaning

def cleantxt(txt):
   
    txt = re.sub(r'@[A-Za-z0-9]+',' ' , txt)
    txt= re.sub(r'RT[\s]+',' ', txt)
    txt= re.sub(r"http\S+", "", txt)
    txt = re.sub(r"[^a-zA-Z#]", " ",txt)
    txt = re.sub(r'#[A-Za-z0-9]+',' ' , txt)
    return txt

### Method to determine Subjectivity and polarity of tweets

def subjective(txt):
    
    return TextBlob(txt).sentiment.subjectivity
    
def polarity(txt):
    
    return TextBlob(txt).sentiment.polarity

### Method to Classify the tweet nature

def poll(p):
    if p > 0 :
        return 'Positive'
    elif p < 0:
        return 'Negative'
    else :
        return 'Neutral'

### Method to Clean tweet text

def lemmatize_text(text):
    return [lemmatizer.lemmatize(w) for w in w_tokenizer.tokenize(text)]

def make_string_from_list(string):
    return ' '.join(string)

### Method for visuallization of tweets

def success(request):

    if request.method=='POST':
        global s_name
        s_name = request.POST['screen_name']
        post = fetch_tweet(s_name)
        for tweet in post[:1]:
            friends_count = tweet.user.friends_count
            p_urll = tweet.user.profile_image_url
        p_url= re.sub('normal','bigger',p_urll)
        
        
        df =pd.DataFrame([tweet.full_text for tweet in post],columns=['Tweets'])
        df['Likes']=[tweet.favorite_count for tweet in post]
        likess=df['Likes'].sum()
        avg_like=df['Likes'].mean()
        
        ####################### Average Tweet Length ##########################
        
        df['Tweet_length']=[tweet.display_text_range[1] for tweet in post]
        
        avg_tweet_length=df['Tweet_length'].mean()
        
        
        ####################### Max like tweet ##############################
        
        max_like=df['Likes'].max()
        max_like_tweet=df[df['Likes']==max_like].iloc[:]['Tweets'].to_list()[0]
        
        ####################### Hash Block ##############################
        
        
        Hash_Tags = df.Tweets.str.findall(r'#.*?(?=\s|$)')

        for i in range(len(Hash_Tags)):
            Hash_Tags[i] = ' '.join(Hash_Tags[i])
  
        df['Hash_Tags'] = Hash_Tags
        
        h=df.Hash_Tags.str.split().tolist()
        h=[j for i in h for j in i]
        
        hash_counts = Counter(h)
        top_hash=hash_counts.most_common(10)
        five_hashes=[val[0] for val in top_hash]
        five_hashes=five_hashes[:5]
        
        all_hash_counts=' '.join(df['Hash_Tags'].tolist())

        value_hash=[val[1] for val in top_hash]
        keys_hash=[key[0] for key in top_hash]
        
        ######################## Mentions Block ########################
        
        mentions = df.Tweets.str.findall(r'@.*?(?=\s|$)')
        for i in range(len(mentions)):
            mentions[i]=' '.join(mentions[i])

        df["Mentions"]=mentions

        a=df.Mentions.str.split().tolist()
        a=[j for i in a for j in i]

        mentions_counts = Counter(a)
        top_mention=mentions_counts.most_common(5)
        five_mentions=[val[0] for val in top_mention]
          
        ################## Follower Count ###################
        
        for tweet in post[:1]:
        
            f_count = tweet.user.followers_count
            #p_url = tweet.user.profile_image_url
        
        ########################## CLEANNG THE TWEET #################
        
        df['Cleaned Tweets']=df['Tweets'].str.lower()
        df["Cleaned Tweets"]=df['Cleaned Tweets'].apply(cleantxt)
        
        ###################### Polarity and Subjectivity ####################
        
        df['Polarity']=df['Tweets'].apply(polarity)
        df['Subjectivity']=df['Tweets'].apply(subjective)
        
        ################# Column for Polarity #######################
        
        df['Poll']=df['Polarity'].apply(poll)
        polarity_counts =(df['Poll'].value_counts()/df['Poll'].count())*100
        polarity_counts=dict(polarity_counts)
        
        dat=dict(df.Poll.value_counts())
        
        ################Lementization################
        
        #df['Cleaned Tweets'] = df['Cleaned Tweets'].apply(lemmatize_text)
        df['Cleaned Tweets'] = df['Cleaned Tweets'].apply(lemmatize_text)
        df['Cleaned Tweets']=df['Cleaned Tweets'].apply(lambda x: [stemmer.stem(i) for i in x])
        
        ################### All Words #################
            
        df['Cleaned Tweets']=df['Cleaned Tweets'].apply(make_string_from_list)
        
        ################### Removal of stop words  and less then 3 length #################
        
        from nltk.corpus import stopwords
        stop = stopwords.words('english')
        
        df['Cleaned Tweets']=df['Cleaned Tweets'].str.split()
        df['Cleaned Tweets']=df['Cleaned Tweets'].apply(lambda x: [item for item in x if item not in stop])
        
        df['Cleaned Tweets']=df['Cleaned Tweets'].apply(make_string_from_list)
        df['Cleaned Tweets'] = df['Cleaned Tweets'].apply(lambda x: ' '.join([i for i in x.split() if len(i)>3]))
        all_words=' '.join(df['Cleaned Tweets'])
        
        context={
        
        'tweet':'tweet',
        'name':s_name,
        'like':likess,
        'fhash':five_hashes,
        'fmention':five_mentions,
        'follow_count':f_count,
        'friends_count':friends_count,
        'max_like':max_like,
        'max_like_tweet':max_like_tweet,
        'avg_tweet_length':avg_tweet_length,
        'avg_like':avg_like,
        'polarity':polarity_counts,
        'img':p_url,
        'all_words':all_words,
        'all_hashes':all_hash_counts,
        'value_hash':value_hash,
        'keys_hash':keys_hash,
        'datapoll':dat
        
        }
    
        return render(request,'success.html',context)
    return render(request,'success.html',context)


    
    
    