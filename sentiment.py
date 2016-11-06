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
subplot = figure.add_subplot(111)
subplot.grid(True)
subplot.set_xlabel('# of Tweets')
subplot.set_ylabel('Net Sentiment')

#Set axis limits.
subplot.set_ylim(-10,10)
subplot.set_xlim(0, 5)
y_min = -10
y_max = 10
x_max = 5

#Plot Variables (# of tweets, net sentiment, x-axis values, y-axis values):
x, y, x_vals, y_vals = 0, 0, np.zeros(0), np.zeros(0) #plot1
x2, y2, x_vals2, y_vals2 = 0, 0, np.zeros(0), np.zeros(0) #plot2

#global vars for keywords to be compared
topic1 = ''
topic2 = ''

#user-defined limit on how many tweets to stream.
tweet_limit = 0
#plot animation
ani = animation.FuncAnimation

#Define a listener class.
class listener(StreamListener):
    def __init__(self, api=None):
        super(listener, self).__init__()
        #Tweet streaming limit.
        self.num_tweets = 0

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
                #Ignore highly objective tweets for sentiment analysis.
                if subjectivity < 0.2:
                    return True

                self.num_tweets += 1
                #If tweet limit is exceeded, then stop stream.
                if self.num_tweets > tweet_limit:
                    global ani
                    ani.event_source.stop()
                    return False

                #To modify global vars:
                global x
                global y
                global x_vals
                global y_vals
                global x2
                global y2
                global x_vals2
                global y_vals2

                #Generate x/y values for graph based on sentiment.
                if topic1.lower() in tweet.lower():
                    x += 1
                    y += polarity
                    x_vals = np.append(x_vals, x)
                    y_vals = np.append(y_vals, y)
                if topic2.lower() in tweet.lower():
                    x2 += 1
                    y2 += polarity
                    x_vals2 = np.append(x_vals2, x2)
                    y_vals2 = np.append(y_vals2, y2)
                #output tweets into file.
                output = open('tweets.txt', 'a')
                output.write(tweet + '::::' + str(polarity))
                output.write('\n')
                output.close()
                return True
            except BaseException as e:
                print('failed on_data', str(e))
        elif 'limit' in data:
            if self.on_limit(json.loads(data)['limit']['track']) is False:
                return False
    def on_error(self, status):
        print('Error on status: ', status)
        #Twitter rate-limiting
        if status == 420:
            return False
    def on_limit(self, status):
        print('Limit threshold exceeded', status)
    def on_timeout(self, status):
        print('Stream disconnected...')

def animate_graph(i):
    p1.set_data(x_vals, y_vals)
    p2.set_data(x_vals2, y_vals2)
    global x
    global y
    global x2
    global y2
    global x_max
    global y_max
    global y_min
    if x > x_max or x2 > x_max:
        x_max = max(x, x2)
        subplot.set_xlim(0, x_max)
    if y > y_max or y2 > y_max:
        y_max = max(y, y2)
        subplot.set_ylim(y_min, y_max)
    if y < y_min or y2 < y_min:
        y_min = min(y, y2)
        subplot.set_ylim(y_min, y_max)
    return p1, p2

if __name__ == '__main__':
    #Handle Twitter authentication.
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    #Connect to Twitter Streaming API
    stream = Stream(auth, listener())
    #Prompt user to enter two keywords to be compared.
    topic1 = input('Enter the first topic: ')
    topic2 = input('Enter the second topic: ')
    tweet_limit = int(input('Enter the # of tweets to stream: '))
    subplot.set_title(topic1 + ' vs. ' + topic2 + ' Twitter Sentiment')
    #Set plots.
    p1, = subplot.plot(x_vals,y_vals,'b-', label=topic1)
    p2, = subplot.plot(x_vals2,y_vals2,'g-', label=topic2)
    #Create legend.
    subplot.legend([p1,p2], [p1.get_label(),p2.get_label()])
    #Clear file of tweets.
    open(filename, 'tweets.txt').close()
    #Filter stream to tweets containing keyword(s). Runs on separate thread.
    stream.filter(track=[topic1, topic2], async=True)
    #Wait for tweets to start streaming.
    time.sleep(2)
    #Plot data.
    ani = animation.FuncAnimation(figure, animate_graph, blit=False, interval=20)
    plt.show()
