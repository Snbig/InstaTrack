'''
Instagram UserID to Username (InstaTrack)
Snippet By Snbig
https://github.com/Snbig/InstaTrack/
'''
import argparse
import hashlib
import json
import re

import requests

parser = argparse.ArgumentParser(prog='InstaTracker.py')

parser.add_argument('-u', '--user', action='store', dest='username',
                    help='Set Instagram username', type=str)
parser.add_argument('-i', '--id', action='store', dest='id',
                    help='Set Instagram userID', type=int)
args = parser.parse_args()


def usernameToUserId(user):
    r1 = requests.get('https://www.instagram.com/web/search/topsearch/?query=' + user, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0'}).text

    try:
        if json.loads(r1)['users'][0]['user']['username'] == user:
            return json.loads(r1)['users'][0]['user']['pk']
    except IndexError:
        return False


def useridToUsername(userid):
    r1 = requests.get('https://instagram.com/instagram/', headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0', }).text
    rhx_gis = json.loads(re.compile('window._sharedData = ({.*?});', re.DOTALL).search(r1).group(1))['nonce']

    ppc = re.search(r'ProfilePageContainer.js/(.*?).js', r1).group(1)
    r2 = requests.get('https://www.instagram.com/static/bundles/es6/ProfilePageContainer.js/' + ppc + '.js').text
    query_hash = re.findall(r'{value:!0}\);const o=\"(.*?)\"', r2)[0]

    query_variable = '{"user_id":"' + str(userid) + '","include_reel":true}'
    t = rhx_gis + ':' + query_variable
    x_instagram_gis = hashlib.md5(t.encode("utf-8")).hexdigest()

    header = {'X-Instagram-GIS': x_instagram_gis,
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0',
              'X-Requested-With': 'XMLHttpRequest'}
    r3 = requests.get(
        'https://www.instagram.com/graphql/query/?query_hash=' + query_hash + '&variables=' + query_variable,
        headers=header).text
    try:
        username = json.loads(r3)['data']['user']['reel']['user']['username']
        return username
    except IndexError:
        return False


if args.id is not None:
    username = useridToUsername(args.id)
    if not username:
        print("[-] UserID does not exist")
    else:
        print("[+] Username: {}".format(username))

if args.username is not None:
    userid = usernameToUserId(args.username)
    if not userid:
        print("[-] Username does not exist")
    else:
        print("[+] UserID: {}".format(userid))
if args.id is None and args.username is None:
    parser.print_help()
