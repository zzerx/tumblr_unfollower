#!/usr/bin/python

import pytumblr
import yaml
import os
import urlparse
import code
import oauth2 as oauth

import time

def new_oauth(yaml_path):
    '''
    Return the consumer and oauth tokens with three-legged OAuth process and
    save in a yaml file in the user's home directory.
    '''

    print 'Retrieve consumer key and consumer secret from http://www.tumblr.com/oauth/apps'
    #consumer_key = raw_input('Paste the consumer key here: ')
    consumer_key = 'p5sps4tytREJ5hvLhF0HUHfGdLopy0MqQwc7J1eIAxiVc4IIl1'
    #consumer_secret = raw_input('Paste the consumer secret here: ')
    consumer_secret = 'GiCErR1C2M2lwgLIZvHYN9IRacbvP6EzISB16kacMazxnyfNTM'

    request_token_url = 'http://www.tumblr.com/oauth/request_token'
    authorize_url = 'http://www.tumblr.com/oauth/authorize'
    access_token_url = 'http://www.tumblr.com/oauth/access_token'

    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)

    # Get request token
    resp, content = client.request(request_token_url, "POST")
    request_token =  urlparse.parse_qs(content)

    # Redirect to authentication page
    print '\nPlease go here and authorize:\n%s?oauth_token=%s' % (authorize_url, request_token['oauth_token'][0])
    redirect_response = raw_input('Allow then paste the full redirect URL here:\n')

    # Retrieve oauth verifier
    url = urlparse.urlparse(redirect_response)
    query_dict = urlparse.parse_qs(url.query)
    oauth_verifier = query_dict['oauth_verifier'][0]

    # Request access token
    token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'][0])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = urlparse.parse_qs(content)

    tokens = {
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret,
        'oauth_token': access_token['oauth_token'][0],
        'oauth_token_secret': access_token['oauth_token_secret'][0]
    }

    yaml_file = open(yaml_path, 'w+')
    yaml.dump(tokens, yaml_file, indent=2)
    yaml_file.close()

    return tokens

def unfollow(client):
    uf = 0
	# usrs = set()
    
    with open ('start.txt', 'r') as f:
	    start = int(f.readline())
	    # print(start)

    for i in range(start,5000,20):
        print(i-uf)
        # print(i-uf, file=f)
        with open ('start.txt', 'w') as f:
            f.writelines(str(i-uf))

        fi = None
        while not fi:
		    try:
		    	fi = client.following(limit=20, offset=i-uf)
		    except Exception as e:
		    	print(e)
		    	print('Connection error, retrying...')
        	
        print('...')
        time.sleep(1)
        if 'blogs' in fi:
            if fi['blogs']:
                for blog in fi['blogs']:
                    if time.time() - blog['updated'] > 1000000:
                        usrurl = blog['url'][7:-1]
                        # usrs.add(usrurl)
                        print('{0} unfollowing {1}'.format(i-uf, usrurl))
                        rt = client.unfollow(usrurl)
                        print(rt)
                        uf += 1
                        time.sleep(1)
            else:
                break
        else:
            print('{0} retrying...'.format(i-uf))
            time.sleep(15)
            continue

    # for usr in usrs:
    #     print('unfollowing {0}'.format(usr))
    #     rt = client.unfollow(usr)
    #     print(rt)
    #     uf += 1
    #     time.sleep(1)

    print('unfollowed {0}'.format(uf))
    print(client.info())
    # print(0,file=f)
    with open ('start.txt', 'w') as f:
        f.writelines(str(0))


if __name__ == '__main__':
    yaml_path = os.path.expanduser('~') + '/.tumblr'

    if not os.path.exists(yaml_path):
        tokens = new_oauth(yaml_path)
    else:
        yaml_file = open(yaml_path, "r")
        tokens = yaml.safe_load(yaml_file)
        yaml_file.close()

    client = pytumblr.TumblrRestClient(
        tokens['consumer_key'],
        tokens['consumer_secret'],
        tokens['oauth_token'],
        tokens['oauth_token_secret']
    )

    #print 'pytumblr client created. You may run pytumblr commands prefixed with "client".\n'

    unfollow(client)

    #code.interact(local=dict(globals(), **{'client': client}))


