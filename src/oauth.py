# -*- coding: utf-8 -*-

import os, sys
import httplib
import time
import Cookie
import uuid
from urllib import urlencode, unquote
from urlparse import urlparse

class Struct:
    def __init__(self, **entries): 
        self.__dict__.update(entries)

class Auth(object):

    def __init__(self):
        self.consumerKey = "suyuxin-9809"
        self.consumerSecret = "f2541e0d8ea719ff"
        self.url = dict()
        self.url["base"]  = "app.yinxiang.com"
        self.url["oauth"] = "/OAuth.action?oauth_token=%s"
        self.url["access"] = "/OAuth.action"
        self.url["token"] = "/oauth"
        self.url["login"] = "/Login.action"

    cookies = {}

    postData = {
        'login': {
            'login': 'Sign in',
            'username': '',
            'password': '',
            'targetUrl': None,
        },
        'access': {
            'authorize': 'Authorize',
            'oauth_token': None,
            'oauth_callback': None,
            'embed': 'false',
        }
    }

    username = None
    password = None
    tmpOAuthToken = None
    verifierToken = None
    OAuthToken = None
    incorrectLogin = 0

    def getTokenRequestData(self, **kwargs):
        params = {
            'oauth_consumer_key': self.consumerKey,
            'oauth_signature': self.consumerSecret+'%26',
            'oauth_signature_method': 'PLAINTEXT',
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': uuid.uuid4().hex
        }

        if kwargs:
            params = dict(params.items() + kwargs.items())
        
        return params
    
    def loadPage(self, url, uri=None, method="GET", params=""):
        if not url:
            print("Request URL undefined")
            return False

        if not uri:
            urlData = urlparse(url)
            url = urlData.netloc
            uri = urlData.path + '?' + urlData.query

        # prepare params, append to uri
        if params :
            params = urlencode(params)
            if method == "GET":
                uri += ('?' if uri.find('?') == -1 else '&') + params
                params = ""

        # insert local cookies in request
        headers = {
            "Cookie": '; '.join( [ key+'='+self.cookies[key] for key in self.cookies.keys() ] )
        }

        if method == "POST":
            headers["Content-type"] = "application/x-www-form-urlencoded"

        conn = httplib.HTTPSConnection(url)
        conn.request(method, uri, params, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()

        print("Response : %s > %s", response.status, response.getheaders())
        result = Struct(status=response.status, location=response.getheader('location', None), data=data)

        # update local cookies
        sk = Cookie.SimpleCookie(response.getheader("Set-Cookie", ""))
        for key in sk:
            self.cookies[key] = sk[key].value

        return result

    def parseResponse(self, data):
        data = unquote(data)
        return dict( item.split('=', 1) for item in data.split('?')[-1].split('&') )


    def getToken(self, username, password):
        print('Authorize...')
        self.getTmpOAuthToken()

        self.login(username, password)

        print('Allow Access...')
        self.allowAccess()

        print('Getting Token...')
        self.getOAuthToken()

        #out.preloader.stop()
        return self.OAuthToken


    def getTmpOAuthToken(self):
        response = self.loadPage(self.url['base'], self.url['token'], "GET", 
            self.getTokenRequestData(oauth_callback="https://"+self.url['base']))

        if response.status != 200:
            print("Unexpected response status on get temporary oauth_token 200 != %s", response.status)
            return False

        responseData = self.parseResponse(response.data)
        if not responseData.has_key('oauth_token'):
            print("OAuth temporary not found")
            return False

        self.tmpOAuthToken = responseData['oauth_token']

        print("Temporary OAuth token : %s", self.tmpOAuthToken)
        return True

    def login(self, username, password):
        response = self.loadPage(self.url['base'], self.url['login'], "GET", {'oauth_token': self.tmpOAuthToken})

        if response.status != 200:
            print("Unexpected response status on login 200 != %s", response.status)
            return False

        if not self.cookies.has_key('JSESSIONID'):
            print("Not found value JSESSIONID in the response cookies")
            return False

        # get login/password
        self.username = username
        self.password = password
        self.postData['login']['username'] = self.username
        self.postData['login']['password'] = self.password
        self.postData['login']['targetUrl'] = self.url['oauth']%self.tmpOAuthToken
        response = self.loadPage(self.url['base'], self.url['login']+";jsessionid="+self.cookies['JSESSIONID'], "POST", 
            self.postData['login'])

        if not response.location and response.status == 200:
            if self.incorrectLogin < 3:
                self.incorrectLogin += 1
                return self.login(username, password)
            else:
                print("Incorrect login or password")

        if not response.location:
            print("Target URL was not found in the response on login")
            return False

        print("Success authorize, redirect to access page")
        return True
        #self.allowAccess(response.location)

    def allowAccess(self):

        self.postData['access']['oauth_token'] = self.tmpOAuthToken
        self.postData['access']['oauth_callback'] = "https://"+self.url['base']
        response = self.loadPage(self.url['base'], self.url['access'], "POST", self.postData['access'])

        if response.status != 302:
            print("Unexpected response status on allowing access 302 != %s", response.status)
            return False

        responseData = self.parseResponse(response.location)
        if not responseData.has_key('oauth_verifier'):
            print("OAuth verifier not found")
            return False

        self.verifierToken = responseData['oauth_verifier']

        print("OAuth verifier token take")
        return True
        #self.getOAuthToken(verifier)

    def getOAuthToken(self):
        response = self.loadPage(self.url['base'], self.url['token'], "GET",  
            self.getTokenRequestData(oauth_token=self.tmpOAuthToken, oauth_verifier=self.verifierToken))

        if response.status != 200:
            print("Unexpected response status on getting oauth token 200 != %s", response.status)
            return False

        responseData = self.parseResponse(response.data)
        if not responseData.has_key('oauth_token'):
            print("OAuth token not found")
            return False

        print("OAuth token take : %s", responseData['oauth_token'])
        self.OAuthToken = responseData['oauth_token']
        return True
