#!/usr/bin/env python
from collections import defaultdict
from datetime import timedelta, datetime
from csv import DictReader
import os

float_cols = ('recent_high', 'last_price', 'first_shaken_price', 'alltime_high',)


def parse_date(s):
    return datetime.strptime(s, '%Y-%M-%d')


def read_data():
    data = []
    for d in DictReader(open('shaken-stocks.csv'), delimiter=';'):
        for c in float_cols:
            d[c] = float(d[c])
        d['first_shaken_at'] = parse_date(d['first_shaken_at'])
        data.append(d)
    return data


def read_sp500_returns():
    last_date = parse_date('2016-01-25')
    prices = { parse_date(d['Date']): float(d['Adj Close'])
               for d in DictReader(open('sp500.csv'), delimiter=',') }
    lp = prices[last_date]
    return { k: (lp - v) / v * 100 for k, v in prices.items() }


_sp500_returns = read_sp500_returns()
def sp500_return(d):
    while 1:
        try:
            return _sp500_returns[d]
        except KeyError:
            d -= timedelta(days=1)


data = read_data()
categories = defaultdict(int)
for d in data:
    sp = d['first_shaken_price']
    recovery = (d['last_price'] - sp) / sp * 100
    market_return = sp500_return(d['first_shaken_at'])

    if recovery < -90:
        categories['wiped out'] += 1
    elif recovery < 0:
        categories['declined'] += 1
    else:
        if recovery < market_return:
            categories['beaten by market'] += 1
        else:
            if recovery == 0:
                categories['even'] += 1
            elif recovery > 1000:
                categories['miracle'] += 1
            elif recovery > 0:
                categories['beat market'] += 1

n = len(data)

print '%-20s: %-10s %-10s %-10s' % ('category', 'count', 'pdf', 'cdf',)
cdf = 0
for k in ('wiped out', 'declined', 'even', 'beaten by market',
          'beat market', 'miracle',):
    p = (float(categories[k]) / n * 100)
    cdf += p
    print '%-20s: %-10s %-10s %-10s' % (k, categories[k], '%.2f%%' % p,
                                        '%.2f%%' % cdf)
