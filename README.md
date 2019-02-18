# speedtest-twitter-bot
Run an internet speed test and send a tweet to your ISP if your speeds are too low.

This script is designed to be run as a cronjob every few minutes on an always-on computer
such as your home server or a raspberry pi. It will test your internet speed and store the
data in a .csv file. Speeds below a certain threshold will trigger a tweet @YourISP.

The speedtest is performed by [speedtest-cli](https://github.com/sivel/speedtest-cli). You will need to have this installed on your machine.

This code makes use of python modules outside the standard library that you also must have installed.
You will need [matplotlib](https://matplotlib.org/), [numpy](https://www.numpy.org/), [pandas](https://pandas.pydata.org/),and [tweepy](https://github.com/tweepy/tweepy).

Linux commands are integral to the code, so you will need to run this on a Linux machine
or virtual environment.

Finally, you will need a Twitter account for which you have keys and access tokens that allow you
to post status updates via the Twitter API. Edit the file "credentials.py" to include your
twitter keys and tokens.

To use this software, place the files in this repository into a common directory and run speedtest_twitter_bot.py.
As stated above, speedtest_twitter_bot.py should be run as cronjob. As written, it is assumed the code will be run
every 5 minutes.

You may need to edit the code based on your ISP and the speeds stipulated in your internet service contract.
In speedtest_twitter_bot.py, do a search for "@Ask_Spectrum" and replace all instances with your ISP's
twitter handle.

This code was written to test a broadband cable internet connection. If you have DSL or fiber
the thresholds in the code will not apply to you. As written, downspeeds less than 30 Mbits/s will trigger
a tweet.  If you search for "30" you will find the sections that define the speed thresholds. Edit these as needed.
You will also find a section where you can edit the contents of your twitter status updates.

In order to make these speedtests fair, do not run this over wifi. You should connect via ethernet to your router.
If you must use wifi, edit the speed thresholds appropriately.
