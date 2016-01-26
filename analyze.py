#!/usr/bin/env python
from collections import defaultdict
from datetime import timedelta, datetime
from csv import DictReader
import os
import sys

check_against_high_price = True

float_cols = ('recent_high', 'last_price', 'first_shaken_price', 'alltime_high',
              'preshake_high',)


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


def log_exceptional(d, r):
    print >>sys.stderr, '%-10s %-40s %.2f' % (d['symbol'], d['name'], r)


def categorize(symbol, last, recovery, market_return, high):
    if recovery < -90:
        return 'wiped out'
    if recovery < 0:
        return 'declined'

    # improvement cases - regardless of how better it got, we should
    # know if the market did better
    if recovery < market_return:
        return 'beaten by market'

    if check_against_high_price:
        if last < high:
            return 'recovered below high price'

    if recovery > 1000:
        return 'miracle'

    return 'beat market'


data = read_data()
categories = defaultdict(int)
for d in data:
    sp = d['first_shaken_price']
    last = d['last_price']
    recovery = (last - sp) / sp * 100
    market_return = sp500_return(d['first_shaken_at'])
    high = d['preshake_high']

    categories[categorize(d['symbol'], last, recovery, market_return, high)] += 1


n = len(data)


if check_against_high_price:
    all_cats = ('wiped out', 'declined', 'beaten by market',
                'recovered below high price', 'beat market', 'miracle',)
else:
    all_cats = ('wiped out', 'declined', 'beaten by market', 'beat market',
                'miracle',)


print
print '%-40s: %-10s %-10s %-10s' % ('category', 'count', 'pdf', 'cdf',)
cdf = 0
for k in all_cats:
    p = (float(categories[k]) / n * 100)
    cdf += p
    print '%-40s: %-10s %-10s %-10s' % (k, categories[k], '%.2f%%' % p,
                                        '%.2f%%' % cdf)
