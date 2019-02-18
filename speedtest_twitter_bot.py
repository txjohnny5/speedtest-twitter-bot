#!/usr/bin/env python
"""
This code is presented under a Creative Commons license.
Use, modify, and distribute as you like.
The author assumes no responsibility for any outcome
resulting from the use of this work or any derivative thereof.
"""
import os
import subprocess
import numpy as np
import pandas as pd
import re
import datetime
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import tweepy
from credentials import * #twitter keys and access tokens

path = '/home/pi/Workspace/speedtest/'

#consistently slow speeds will trigger the creation
#of a graph which will be included in a status update.
def graph_speed():
	df = pd.read_csv(path + 'data.csv', index_col=False,
					names=["Down","Up","Timestamp"])
	
	plt.figure(figsize=(16,9))
	plt.style.use(['dark_background'])
	ax = plt.subplot2grid((1,1),(0,0))
	
	ax.xaxis.set_ticks(np.arange(0,len(df["Down"])))
	
	#set x-axis tick labels
	a = ax.get_xticks().tolist()
	for x in range(0,len(df["Down"])):
		#display only every nth x-axis tick label
		if x % 10 == 0:
			a[x] = df.iloc[x]["Timestamp"]
		else:
			a[x] = " "
	ax.set_xticklabels(a)
	
	#rotate x-tick labels for better fit
	ticks = ax.get_xticklabels()
	for label in ticks:
		label.set_rotation(78) #units here are degrees
		label.set_x(-0.5) #shift x-tick labels to the left
		label.set_fontsize(11)

	#turn xticks off. plot title and y-axis labels
	plt.tick_params(axis='x',which='both',bottom=False,top=False)
	plt.title("Charter Spectrum Consumer Internet Down/Up Speeds",fontsize=20)
	plt.ylabel("Connection Speed (Mbits/s)",fontsize=18)
	#set ylim based on your connection speed.
	#for example, I nominally get ~70Mbits/s,
	#so 90 is a good y-axis limit for me.
	plt.ylim(0,90)
	
	#draw plot for up/down speeds
	ax.plot(np.arange(0,len(df)),df["Down"].values,
			color="#00FFFF",linewidth=2,zorder=2)
	ax.plot(np.arange(0,len(df)),df["Up"].values,
			color="#00FF00",linewidth=2,zorder=2)
	
	#remove verticle grid lines
	ax.yaxis.grid(True,zorder=0)

	#label plotted lines
	ax.annotate("DownSpeed",xy=(0.1,77),xytext=(0.1,77),
				color="#00FFFF",weight="bold",fontsize=14)
	ax.annotate("UpSpeed",xy=(0.1,15),xytext=(0.1,15),
				color="#00FF00",weight="bold",fontsize=14)
	
	plt.subplots_adjust(right=0.95,left=0.09,bottom=0.22)
	
	#make full-screen chart by default
	mng = plt.get_current_fig_manager()
	mng.full_screen_toggle()
	
	#save pot to file
	plt.savefig(path + 'speed_plot.png', )

	#uncomment if you want to display plot on screen
	#plt.show()

def main():
	#variable names in "credentials.py" must match those passed bellow
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)
	try:
		#pipe results of speedtest to grep to find lines which contain
		#"load:" i.e. "upload:" and "download:" write those lines to a file
		os.system('speedtest | grep load: > ' + path + 'speedNow.txt')
		
		#clean up grep's output
		lines = [line.rstrip('\n') for line in open(path + 'speedNow.txt')]
		
		downs = lines[0].split(": ")
		ups   = lines[1].split(": ")
		
		down  = downs[1].split(" ")
		up    = ups[1].split(" ")
		
		#what's left are floats representing upload and download speeds
		downSpeed = down[0]
		upSpeed   = up[0]
		
		#timestamp
		dt  = str(datetime.datetime.now())
		now = dt[:-7]
		
		#put it all together and store it in a pandas dataframe
		results = []
		results.append(downSpeed)
		results.append(upSpeed)
		results.append(now)
		df = pd.DataFrame(results).T
		
		#historical data lives in "data.csv." append latest results to that file
		df.to_csv(path + 'data.csv',mode='a',header=False,index=False)
		
		#load updated data.csv as new dataframe
		dat = pd.read_csv(path + 'data.csv',index_col=False,
						 names=['Down','Up','Timestamp'])
		
		#retrieve latest downspeed result
		lastDown = dat.iloc[-1]['Down']
		lastTime = str(dat.iloc[-1]['Timestamp'])
		
		#compose tweet. Content will depend on measured downspeed.
		tw = open(path + 'newTweet.txt', 'w')
		if float(lastDown) < 30 and float(lastDown) >= 20:
			tw.write('@Ask_Spectrum This is too slow.\n')
		if float(lastDown) < 20 and float(lastDown) >= 14:
			tw.write('@Ask_Spectrum You really must do better.\n')
		if float(lastDown) < 14 and float(lastDown) >= 8:
			tw.write("@Ask_Spectrum I'm not angry. I'm just dissappointed.\n")
		if float(lastDown) < 8 and float(lastDown) >= 2:
			tw.write("@Ask_Spectrum I'm not paying DSL prices. " +
					"Why am I getting DSL speed?\n")
		if float(lastDown) < 2 and float(lastDown) > 0:
			tw.write('@Ask_Spectrum DIAL-UP SPEED WILL NOT SILENCE ME!\n')
		else:
			pass
		tw.close()
		
		#include speedtest results in the tweet
		tw = open(path + 'newTweet.txt', 'a')
		tw.write('Downspeed: ' + str(lastDown) + ' Mbits/s\n')
		tw.write('Measured on ' + str(lastTime) + '\n\n')
		tw.write('#GetWhatYouOverpayFor')
		tw.close()
		
		#prep tweet
		with open(path + 'newTweet.txt', 'r') as tweetFile:
			content = tweetFile.read()
		
		#update twitter status
		if float(lastDown) < 30:
			api.update_status(content)
		
			#each time a tweet is sent, add a line to a text file.
			#counting lines allows us to keep track of how many tweets
			#have been sent. Below we'll combine this information with
			#tweet frequency to determine whether to tweet a graph.
			os.system('echo 0 >> ' + path + 'tweetCount.txt')
			#get number of lines in "tweetcount.txt" and store
			#the number in variable "tweetCount"
			proc = subprocess.Popen('cat ' + path + 'tweetCount.txt | wc -l',
									shell=True, stdout=subprocess.PIPE)
			tweetCount = str(proc.communicate()[0])
			tweetCount = re.sub("[^0-9]", "", tweetCount)
			"""
			once enough data has been accumulated, check how often
			low speeds trigger a tweet. If enough tweets are sent
			within a specified time interval, create a graph of speeds
			over that time and include it in a status update.
		
			the number in the if statement below is based on how often this
			script is run.  Assuming it runs every 5 minutes, 864 entries
			would represent 3 days of data.
			"""
			if len(dat) > 863:
				offenders = []
				last3days = dat[-863:]
				for i in range(0,len(last3days)):
					if last3days.iloc[i]['Down'] < 30:
						offenders.append(round(dat.iloc[i]['Down'],2))
				#if more than 20 tweets have been sent in the last 3 days, e.g.,
				#create the graph and include it in a status update.
				if int(tweetCount) > 20 and len(offenders) > 20:
					graph_speed()
					#full path to newly created graph
					imagePath = '/home/pi/Workspace/speedtest/speed_plot.png'
					try:
						tw = '@Ask_Spectrum Here is a graph showing how poor my service has been lately.\n\n#GetWhatYouOverpayFor'
						status = api.update_with_media(imagePath,tw)
						api.update_status(status)
		
						#reset the tweet count after posting a graph.
						os.system('rm ' + path + 'tweetCount.txt')
					except Exception:
						pass

	except Exception:
		#something failed, probably no internet connection.
		#this script assumes it's the ISP's fault.
		dt = str(datetime.datetime.now())
		now = dt[:-7]
	
		#write zeroes to data.csv
		results = []
		results.append('0')
		results.append('0')
		results.append(now)
	
		dfail = pd.DataFrame(results).T
		dfail.to_csv(path +'data.csv',mode='a',header=False,index=False)

main()
