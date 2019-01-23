import json
import requests
import re
import hashlib


def usernameToUserId(user):
    r1 = requests.get('https://www.instagram.com/web/search/topsearch/?query=' + user, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0'}).text

    if json.loads(r1)['users'][0]['user']['username'] == user:
        return json.loads(r1)['users'][0]['user']['pk']


def useridToUsername(id):
    if str(id).isnumeric():
        r1 = requests.get('https://instagram.com/instagram/', headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0', }).text
        rhx_gis = json.loads(re.compile('window._sharedData = ({.*?});', re.DOTALL).search(r1).group(1))['rhx_gis']

        ppc = re.search(r'ProfilePageContainer.js/(.*?).js', r1).group(1)
        r2 = requests.get('https://www.instagram.com/static/bundles/metro/ProfilePageContainer.js/' + ppc + '.js').text
        query_hash = re.findall(r'{value:!0}\);var u=\"(.*?)\"', r2)[0]

        query_variable = '{"user_id":"' + str(id) + '","include_reel":true}'
        t = rhx_gis + ':' + query_variable
        x_instagram_gis = hashlib.md5(t.encode("utf-8")).hexdigest()

        header = {'X-Instagram-GIS': x_instagram_gis,
                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0',
                  'X-Requested-With': 'XMLHttpRequest'}
        r3 = requests.get(
            'https://www.instagram.com/graphql/query/?query_hash=' + query_hash + '&variables=' + query_variable,
            headers=header).text

        username = json.loads(r3)['data']['user']['reel']['user']['username']
        return username
