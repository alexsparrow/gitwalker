#!/usr/bin/env python
import datetime
import json

from pylab import *
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook
from matplotlib.dates import  DateFormatter, WeekdayLocator, HourLocator, \
     DayLocator, MONDAY

def data_dummy():
    return [
        {"date": datetime.datetime.now(),
         "count": 100}
        ]

def data_real(path):
    d = json.load(open(path, "r"))
    dts = {}
    for x in d:
        dt = datetime.datetime.strptime(x["date"], "%d/%m/%Y")
        if isinstance(x["result"], basestring):
            val = int(x["result"])
            if not dt in dts or val > dts[dt]: dts[dt] = val
    return sorted([{"date":d, "count":c} for d, c in dts.iteritems()], key=lambda x:x["date"])



def plot(data):
    dates = [x["date"] for x in data]
    counts = [x["count"] for x in data]
    mindate, maxdate = min(dates), max(dates)
    daterange = maxdate - mindate

    monthdays = mdates.DayLocator(bymonthday = (1, 15))
    monthdays2 = mdates.DayLocator(bymonthday = (1,))
    mondays    = mdates.WeekdayLocator(byweekday=MONDAY)
    alldays    = DayLocator()              # minor ticks on the days
    weekFormatter = DateFormatter('%d/%m/%Y')  # Eg, Jan 12
    dayFormatter = DateFormatter('%d')      # Eg, 12

    # load a numpy record array from yahoo csv data with fields date,
    # open, close, volume, adj_close from the mpl-data/example directory.
    # The record array stores python datetime.date as an object array in
    # the date column
    # datafile = cbook.get_sample_data('goog.npy')
    # r = np.load(datafile).view(np.recarray)

    fig = plt.figure()
    fig.subplots_adjust(bottom=0.2)
    ax = fig.add_subplot(111)
    ax.plot(dates, counts)
    ax.grid()
    ax.semilogy()
    # format the ticks
    if daterange.days > 200:
        ax.xaxis.set_major_locator(monthdays2)
    elif daterange.days > 100:
        ax.xaxis.set_major_locator(monthdays)
    else:
        ax.xaxis.set_major_locator(mondays)
    ax.xaxis.set_minor_locator(alldays)
    ax.xaxis.set_major_formatter(weekFormatter)

    # datemin = datetime.date(r.date.min().year, 1, 1)
    # datemax = datetime.date(r.date.max().year+1, 1, 1)
    # ax.set_xlim(datemin, datemax)
    ax.xaxis_date()
    ax.autoscale_view()
    setp( gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    ax.set_xlabel("Date")
    ax.set_ylabel("Word Count")
    fig.savefig("out.pdf")

if __name__ == "__main__":
    #    plot(data_dummy())
    plot(data_real("out.json"))
