from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
from textblob import TextBlob
import matplotlib.pyplot as plt
import time
import matplotlib.animation as animation
import numpy as np

#User credentials for Twitter API
consumer_key = 'YSVkMY3uFU8Y3fjeXezFcBD72'
consumer_secret = 'Csm5fPjuDyJNlzY2QJJRPgtI5VTJL6IXTsY7L9YorojJC1y9AK'
access_token = '409752074-E38Wc8WF8bc0jst4NridK07hnfUuEX4LYDjQYc0o'
access_token_secret = 'yqdvl8dtNWj8fDUEcZkg7Afz04pqEHfKMlKKKupUE6PAV'

font = {'size'   : 9}
plt.rc('font', **font)

#Emulates aesthetics of ggplot - a plotting package in R.
plt.style.use("ggplot")

#Setup figure and plot.
figure = plt.figure()
subplot = figure.add_subplot(211)
subplot.grid(True)
subplot.set_xlabel('# of Tweets')
subplot.set_ylabel('Net Sentiment')

subplot2 = figure.add_subplot(212)
subplot2.grid(True)
subplot2.set_xlabel('# of Tweets')
subplot2.set_ylabel('Net Sentiment')

#global vars for keywords to be compared
topic1 = ''
topic2 = ''

#Define a listener class.
class listener(StreamListener):

    def on_data(self, data):
        if 'text' in data:
            try:
                #Extract tweet text.
                tweet = json.loads(data)['text']
                tb = TextBlob(tweet)
                #Polarity is a float between -1 and 1 (negative and positive).
                polarity = tb.sentiment.polarity
                #Subjectivity is a float from 0 (very objective) to 1 (very subjective)
                subjectivity = tb.sentiment.subjectivity

                #Write sentiment to respective file.
                if topic1.lower() in tweet.lower():
                    print('topic1')
                    output = open('topic1.txt', 'a')
                    output.write(str(polarity))
                    output.write('\n')
                    output.close()
                if topic2.lower() in tweet.lower():
                    print('topic2')
                    output = open('topic2.txt', 'a')
                    output.write(str(polarity))
                    output.write('\n')
                    output.close()
                #print(tweet, '::', str(polarity))
                return True
            except BaseException as e:
                print('failed on_data', str(e))
                #print('tweet: ', data)
                time.sleep(10)
        elif 'limit' in data:
            print('LIMIT FOUND')
            if self.on_limit(json.loads(data)['limit']['track']) is False:
                return False

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

    #Plot Variables (# of tweets, net sentiment, x-axis values, y-axis values):
    x, y, x_vals, y_vals = 0, 0, [], [] #plot1
    x2, y2, x_vals2, y_vals2 = 0, 0, [], [] #plot2

    #Generate x/y values for graph based on sentiment.
    for line in lines:
        line = line.strip()
        ##only read line if not blank
        if(line):
            x += 1
            y += float(line)
            x_vals.append(x)
            y_vals.append(y)

    for line in lines2:
        line = line.strip()
        if(line):
            x2 += 1
            y2 += float(line)
            x_vals2.append(x2)
            y_vals2.append(y2)

    subplot.clear()
    subplot.plot(x_vals, y_vals, 'g-')
    subplot2.clear()
    subplot2.plot(x_vals2, y_vals2, 'b-')


if __name__ == '__main__':
    #Handle Twitter authentication.
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    #Connect to Twitter Streaming API
    stream = Stream(auth, listener())
    #Prompt user to enter two keywords to be compared.
    topic1 = input('Enter the first topic: ')
    topic2 = input('Enter the second topic: ')
    figure.suptitle(topic1+' vs. '+topic2+' Twitter Sentiment', fontsize=12)
    #Filter stream to tweets containing keyword(s). Runs on separate thread.
    stream.filter(track=[topic1, topic2], async=True)
    #Wait for tweets to start streaming.
    time.sleep(5)
    #Plot data.
    ani = animation.FuncAnimation(figure, animate_graph, interval=5)
    plt.show()
