from django.shortcuts import render
from django.views.generic import TemplateView
from polls.forms import HomeForm


from bigquery import get_client
import re

from google.cloud import bigquery
from django.core.files import File
from tweepy import OAuthHandler
from textblob import TextBlob
import tweepy
import csv #Import csv

# Create your views here.


class HomeView(TemplateView):
    template_name = 'polls/index.html'
    pname = ' '

    def clean_tweet(tweet):

        # Utility function to clean tweet text by removing links, special characters
        # using simple regex statements.

        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w+:\ / \ / \S+)", " ", tweet).split())

    def get_tweet_sentiment(tweet):

        # Utility function to classify sentiment of passed tweet
        # using textblob's sentiment method

        # create TextBlob object of passed tweet text
        analysis = TextBlob(HomeView.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(api, query, count=10):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = api.search(q=query, count=1000)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = HomeView.get_tweet_sentiment(tweet.text)

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            # return parsed tweets
            return tweets
        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))

    def requestHandler(api, pname):

        #print("Debug requestHandler: "+ str(api))
        # calling function to get tweets
        tweets = HomeView.get_tweets(api, query=pname, count=1000)

        # picking positive tweets from tweets
        ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
        # percentage of positive tweets
        positive1 = 100 * len(ptweets) / len(tweets)
        print("Positive tweets percentage: {} %".format(100 * len(ptweets) / len(tweets)))
        # picking negative tweets from tweets
        ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
        negative1 = 100 * len(ntweets) / len(tweets)
        # percentage of negative tweets
        print("Negative tweets percentage: {} %".format(100 * len(ntweets) / len(tweets)))
        # percentage of neutral tweets
        neutral = [tweet for tweet in tweets if tweet['sentiment'] == 'neutral']
        neutral1 = 100 * (len(tweets) - len(ntweets) - len(ptweets)) / len(tweets)
        print("Neutral tweets percentage: {} %".format(
            100 * (len(tweets) - len(ntweets) - len(ptweets)) / len(tweets)))

        # printing first 5 positive tweets
        print("\n\nPositive tweets:")
        for tweet in ptweets[:50]:
            print(tweet['text'])

        # printing first 5 negative tweets
        print("\n\nNegative tweets:")
        for tweet in ntweets[:50]:
            print(tweet['text'])

        print("\n\nNeutral tweets tweets:")
        for tweet in neutral[:50]:
            print(tweet['text'])
        project_id = 'lithe-realm-202706'
        #service_account = 'twitter@lithe-realm-202706.iam.gserviceaccount.com'
        #json_key = '/Users/DELL/Desktop/amishapro/Tweets-e0732831d21d.json'
        print("check")
        # client = get_client(json_key_file=json_key, readonly=False)

        client = bigquery.Client(project=project_id)
        # Prepares a reference to the new dataset
        dataset_id = pname + 'dataset'
        dataset_ref = client.dataset(dataset_id)
        dataset = bigquery.Dataset(dataset_ref)

        # Creates the new dataset

        dataset = client.create_dataset(dataset)

        print('Dataset {} created.'.format(dataset.dataset_id))
        schema = {


            bigquery.SchemaField('Tweet', 'STRING')


        }

        table_ref = dataset_ref.table('Positive')
        table = bigquery.Table(table_ref, schema=schema)
        table = client.create_table(table)

        assert table.table_id == 'Positive'

        i =0
        postweet = []
        for tweet in ptweets[:50]:
            postweet.append((tweet['text'], i))
            i += 1
            # client.insert_rows_json(table_ref,tweet['text'])
        # job=client.
        #print('\n \n \n ' + str(postweet))
        client.insert_rows(table_ref, postweet, selected_fields=schema)
        #assert job == []


        table_ref = dataset_ref.table('Negative')
        table = bigquery.Table(table_ref, schema=schema)
        table = client.create_table(table)

        assert table.table_id == 'Negative'

        i = 0
        negtweet = []
        for tweet in ntweets[:50]:
            negtweet.append((tweet['text'], i))
            i += 1
            # client.insert_rows_json(table_ref,tweet['text'])
            # job=client.
            # print('\n \n \n ' + str(postweet))
        client.insert_rows(table_ref, negtweet, selected_fields=schema)


        table_ref = dataset_ref.table('Neutral')
        table = bigquery.Table(table_ref, schema=schema)
        table = client.create_table(table)

        assert table.table_id == 'Neutral'

        i = 0
        neutweet = []
        for tweet in neutral[:50]:
            neutweet.append((tweet['text'], i))
            i += 1
            # client.insert_rows_json(table_ref,tweet['text'])
            # job=client.
            # print('\n \n \n ' + str(postweet))
        client.insert_rows(table_ref, neutweet, selected_fields=schema)

        Message = '' + str(positive1) + ',' + str(negative1) + ',' + str(neutral1)
        return Message

    def get(self, request):
        form = HomeForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = HomeForm(request.POST)
        Message = ' '

        if form.is_valid():
            pname = form.cleaned_data['name']
            print(pname)

            try:
                    # keys and tokens from the Twitter Dev Console
                    consumer_key = 'XYxB9c8OZ42hj8LHMO26J6tjg'
                    consumer_secret = 'tyZ0hoXRNKhPpmDHtgAQbaP2HELoEAyeUpoIiYWNTylv1b7KZA'
                    access_token = '955562395530813440-hmjqN1ZrdQXZgHUAPotZBzpbA2J36bg'
                    access_token_secret = 'fccDpYLFNsjcHMvMOyuN3Y6bNwC9TXPFnno7UUTkPx22S'

                    # create OAuthHandler object
                    auth = OAuthHandler(consumer_key, consumer_secret)
                    # set access token and secret
                    auth.set_access_token(access_token, access_token_secret)
                    # create tweepy API object to fetch tweets
                    api = tweepy.API(auth)
                    print(api)
                    Message = HomeView.requestHandler(api, pname)

            except tweepy.TweepError as e:
                    # print error (if any)
                    print("Error : " + str(e))

            context = {'message': Message}
            print(context)
            return render(request, 'polls/result.html', context)
