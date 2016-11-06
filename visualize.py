from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
from textblob import TextBlob
import pandas as pd
import matplotlib.pyplot as plt
import time
import matplotlib.animation as animation


#User credentials for Twitter API
consumer_key = 'YSVkMY3uFU8Y3fjeXezFcBD72'
consumer_secret = 'Csm5fPjuDyJNlzY2QJJRPgtI5VTJL6IXTsY7L9YorojJC1y9AK'
access_token = '409752074-E38Wc8WF8bc0jst4NridK07hnfUuEX4LYDjQYc0o'
access_token_secret = 'yqdvl8dtNWj8fDUEcZkg7Afz04pqEHfKMlKKKupUE6PAV'

#Create a plot using pyplot.
figure = plt.figure()
#Create a subplot
subplot = figure.add_subplot(111)
#Emulates aesthetics of ggplot - a plotting package in R.
plt.style.use("ggplot")

#global vars for keywords to be compared
topic1, topic2 = '', ''

#Define a listener class.
class listener(StreamListener):

    def on_data(self, data):
        try:
            #Extract tweet text.
            tweet = json.loads(data)['text']
            tb = TextBlob(tweet)
            #Polarity is a float between -1 and 1 (negative and positive).
            polarity = tb.sentiment.polarity
            #Subjectivity is a float from 0 (very objective) to 1 (very subjective)
            subjectivity = tb.sentiment.subjectivity

            #Write sentiment to file.
            output = file()
            if topic1 in tweet:
                output = open('topic1.txt', 'a')
            elif:
                output = open('topic2.txt', 'a')
            output.write(str(polarity))
            output.write('\n')
            output.close()
            return True
        except BaseException as e:
            print('failed on_data', str(e))

    def on_error(self, status):
        print(status)
        #Twitter rate-limiting
        if status == 420:
            return False

def animate_graph(i):
    data = open('topic1.txt', 'r').read()
    lines = data.split('\n')
    data2 = open('topic2.txt', 'r').read()
    lines2 = data.split('\n')

    #first topic:
    x = 0 # Number of tweets.
    y = 0 # Cumulative sentiment.
    x_vals = [] # Values to plot.
    y_vals = []

    #second topic:
    x2, y2, x_vals2, y_vals2 = 0, 0, [], []

    #Generate x/y values for graph based on sentiment.
    for line in lines:
        line = line.strip()
        if(line):
            tweet = line.split('::::')[0]
            sentiment = line.split('::::')[1]
            if topic1 in tweet:
                x += 1
                y += float(sentiment)
                x_vals.append(x)
                y_vals.append(y)
            elif topic2 in tweet:
                x2 += 1
                y2 += float(sentiment)
                x_vals2.append(x2)
                y_vals2.append(y2)

    #Plot x/y values.
    subplot.clear()
    subplot.plot(x_vals, y_vals, 'r-', label=topic1)
    subplot.plot(x_vals2, y_vals2, 'b-', label=topic2)

if __name__ == '__main__':
    #Handle Twitter authentication.
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    #Connect to Twitter Streaming API
    twitterStream = Stream(auth, listener())
    #Prompt user to enter two keywords to be compared.
    topic1 = input('Enter the first topic: ')
    topic2 = input('Enter the second topic: ')
    #Filter stream to tweets containing keyword(s). Runs on separate thread.
    twitterStream.filter(track=[topic1, topic2], async=True)
    #Plot data.
    ani = animation.FuncAnimation(figure, animate_graph, interval=100)
    plt.show()
