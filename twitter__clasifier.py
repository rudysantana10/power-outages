# -*- coding: utf-8 -*-
import sys
import csv
import couchdb
from string import punctuation
from couchdb.mapping import Document

def strip_punctuation(s):
    return ''.join(c for c in s if c not in punctuation)

def classifier(str):
    tweet = str.lower()
#    tweet = str.lower().split()
#    tweet = strip_punctuation(tweet)

    if (tweet.count('flickering') <= 0):
        if (tweet.count('you') <= 0):
            if (tweet.count('electricity') <= 0):
                return 'PO'
            else:
                if (tweet.count('bill') <= 0):
                    if (tweet.count('had') <= 0):
                        if (tweet.count('via') <= 0):
                            if (tweet.count('like') <= 0):
                                if (tweet.count('by') <= 0):
                                    return 'PO'
                                else:
                                    if (tweet.count('my') <= 0):
                                        return 'NP'
                                    else:
                                        return 'PO'
                            else:
                                return 'NP'
                        else:
                            return 'NP'
                    else:
                        return 'NP'
                return 'NP'
        else:
            if (tweet.count('2016') <= 0):
                if (tweet.count('imagine') <= 0):
                    if (tweet.count('is') <= 0):
                        if (tweet.count('no') <= 0):
                            return 'PO'
                        else:
                            if (tweet.count('with') <= 0):
                                return 'PO'
                            else:
                                return 'NP'
                    else:
                        return 'PO'
                else:
                    return 'NP'
            else:
                return 'NP'
    else:
        if (tweet.count('christmas') <= 0):
            if (tweet.count('her') <= 0):
                if (tweet.count('they') <= 0):
                    if (tweet.count('what') <= 0):
                        return 'PL'
                    else:
                        return 'NP'
                else:
                    return 'NP'
            else:
                return 'NP'
        else:
            return 'NP'
