#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

#
# Copyright 2012 Onur Gungor <onurgu@boun.edu.tr>
# Derived from sna-tools for direnaj

# TODO: move this to direnaj/plugins/streamers in the future. I'm not
# moving it there already due to request.

import oauth2 as oauth
import pymongo

import sys, threading, time, datetime
import pycurl
import urllib
import os
import bson.json_util

# local
from config import *

# We should ignore SIGPIPE when using pycurl.NOSIGNAL - see
# the libcurl tutorial for more info.
try:
    import signal
    from signal import SIGPIPE, SIG_IGN
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
except ImportError:
    pass

class StreamCatcher(threading.Thread):
    def __init__(self, url = "", postdata = {}, keystore = KeyStore()):

        # required for threads
        super(StreamCatcher, self).__init__()

        if url == "":
            self.filter_url = "https://stream.twitter.com/1.1/statuses/filter.json"
        else:
            self.filter_url = url

        self.prev_buf = ''

        self.direnaj_auth_secrets = keystore.direnaj_auth_secrets.copy()

        token = oauth.Token(key=keystore.access_token_key,
                            secret=keystore.access_token_secret)
        consumer = oauth.Consumer(key=keystore.app_consumer_key,
                                  secret=keystore.app_consumer_secret)

        signature_method = oauth.SignatureMethod_HMAC_SHA1()

        params = {
                'oauth_version': "1.0",
                'oauth_nonce': oauth.generate_nonce(),
                'oauth_timestamp': int(time.time())
        }

        # Set our token/key parameters
        params['oauth_token'] = token.key
        params['oauth_consumer_key'] = consumer.key

        # prepare POST request on our own.
        for key, value in postdata.items():
            params[key] = value

        req = oauth.Request(method="POST",
                            url=self.filter_url,
                            parameters=params,
                            is_form_encoded=True)

        # Sign the request.
        req.sign_request(signature_method, consumer, token)

        header = req.to_header(realm='Firehose')

        # set libcurl options
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.URL, self.filter_url)
        # set to 0 for removing the header
        # self.curl.setopt(pycurl.HEADER, 1)
        self.curl.setopt(pycurl.HTTPHEADER,
                        ['Authorization: ' + str(header['Authorization'])])
        # self.curl.setopt(pycurl.WRITEDATA, self.ofile)
        self.curl.setopt(pycurl.WRITEFUNCTION, self.writefunction)
        self.curl.setopt(pycurl.FOLLOWLOCATION, 1)
        self.curl.setopt(pycurl.MAXREDIRS, 5)
        self.curl.setopt(pycurl.NOSIGNAL, 1)
        self.curl.setopt(pycurl.NOPROGRESS, 0)
        self.curl.setopt(pycurl.PROGRESSFUNCTION, self.progress)
        if len(postdata) != 0:
            self.curl.setopt(pycurl.POSTFIELDS,
                            urllib.urlencode(postdata))

        self.abortEvent = threading.Event()

    def datetime_hook(self, dct):
        if 'created_at' in dct:
            time_struct = time.strptime(dct['created_at'], "%a %b %d %H:%M:%S +0000 %Y") #Tue Apr 26 08:57:55 +0000 2011
            dct['created_at'] = datetime.datetime.fromtimestamp(time.mktime(time_struct))
            return dct
        return dct

    def writefunction(self, buf):

        print buf
        # mongo
        self.prev_buf = self.prev_buf + buf

        import requests

        if '\r\n' in self.prev_buf:
           parts = self.prev_buf.split('\r\n')
           if len(parts) > 1:
               tmp = []
               for p in parts[0:-1]:
                   if len(p) > 0:
                       # obj = json.loads(p, object_hook=self.datetime_hook)
                       tmp.append(bson.json_util.loads(p))
               if len(tmp) > 0:
                   direnaj_store_url = 'http://'+DIRENAJ_APP_HOST+':'+str(DIRENAJ_APP_PORT[DIRENAJ_APP_ENVIRONMENT])+'/statuses/store'
                   params = {'tweet_data': bson.json_util.dumps(tmp)}
                   params.update(self.direnaj_auth_secrets)

                   print params
                   response = requests.post(direnaj_store_url,
                                            params=params)
                   print response.content
               self.prev_buf = parts[-1]
           else:
               obj = [bson.json_util.loads(parts[0])]

               params = {'tweet_data': bson.json_util.dumps(obj)}
               params.update(self.direnaj_auth_secrets)

               print params
               response = requests.post(direnaj_store_url,
                                            params=params)
               self.prev_buf = ''

    def run(self):
        try:
            self.curl.perform()
            self.curl.close()
        except Exception, e:
            # callback aborted
            if e[0] == 42:
                print "callback aborted"
            # gnutls: a tls packet with unexpected size is received.
            elif e[0] == 56:
                print "tls packet with unexpected size"
            else:
                raise
        sys.stdout.write(".")
        sys.stdout.flush()

    def progress(self, download_t, download_d, upload_t, upload_d):
        pass

    def join(self, command='', timeout=None):
        if command == 'stop':
            self.abortEvent.set()
            super(StreamCatcher, self).join(timeout)

if __name__ == "__main__":

    if len(sys.argv) > 1:
        user_input = sys.argv[1]
    else:
        user_input = "türkiye"
    threads = []
    # Start one thread per URI in parallel
    t1 = time.time()
    t = StreamCatcher(
            postdata={"track": user_input})
    t.start()
    threads.append(t)
    for thread in threads:
        thread.join('stop')
        t2 = time.time()
        print "\n** Multithreading, %d seconds elapsed" % (int(t2-t1))