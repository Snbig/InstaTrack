'''
Instagram UserID to Username (InstaTrack)
Snippet By Snbig
https://github.com/Snbig/InstaTrack/
'''
import argparse, hashlib, json, re, requests

authtokens = tuple()

def checkTokens():
    if not authtokens:
        getTokens()


def getTokens():
    r = requests.get('https://instagram.com/', headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0', }).text
    rhx_gis = json.loads(re.compile('window._sharedData = ({.*?});', re.DOTALL).search(r).group(1))['nonce']

    ppc = re.search(r'ConsumerLibCommons.js/(.*?).js', r).group(1)
    r = requests.get('https://www.instagram.com/static/bundles/metro/ConsumerLibCommons.js/' + ppc + '.js').text
    query_hash = re.findall(r'{value:!0}\);(?:var|const|let) .=\"([0-9a-f]{32})\"', r)[1]

    global authtokens
    authtokens = tuple((rhx_gis, query_hash))


def const_gis(query):
    checkTokens()
    t = authtokens[0] + ':' + query
    x_instagram_gis = hashlib.md5(t.encode("utf-8")).hexdigest()
    return x_instagram_gis


def usernameToUserId(user):
    r = requests.get('https://www.instagram.com/web/search/topsearch/?query=' + user, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0'}).text

    if json.loads(r).get("message") == 'rate limited':
        print(
            '[x] Rate limit reached!\n[#] Unchecked Username: {}\n[!] Try again in a few minutes.\n'.format(user))
        exit()

    try:
        for i in range(len(json.loads(r)['users'])):
            if json.loads(r)['users'][i]['user']['username'] == user:
                return json.loads(r)['users'][i]['user']['pk']
    except IndexError:
        return False


def useridToUsername(userid):
    header = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 Instagram 12.0.0.16.90 (iPhone9,4; iOS 10_3_3; en_US; en-US; scale=2.61; gamut=wide; 1080x1920)',
        'X-Requested-With': 'XMLHttpRequest'}
    r = requests.get(
        f'https://i.instagram.com/api/v1/users/{userid}/info/',
        headers=header).text
    if json.loads(r).get("status") != 'ok':
        print('[x] Rate limit reached!\n[#] Unchecked ID: {}\n[!] Try again in a few minutes..\n'.format(userid))
        exit()
    try:
        return json.loads(r)['user']['username']
    except IndexError:
        return False


def main():
    parser = argparse.ArgumentParser(prog='InstaTracker.py')

    parser.add_argument('-u', '--user', action='store', dest='username',
                        help='Set Instagram username', type=str)
    parser.add_argument('-i', '--id', action='store', dest='id',
                        help='Set Instagram userID', type=int)
    parser.add_argument('-f', '--list', action='store', dest='file',
                        help='Import username/userID per line as .txt file',
                        type=str)
    args = parser.parse_args()

    if args.file is not None:
        result = list()

        try:
            with open(args.file, 'r') as file:
                elements = file.readlines()
        except FileNotFoundError:
            print('[-] File Not Found :(')
            return 0

        print("Processing...\n")
        with open('result.txt', 'w') as file:
            for e in elements:
                e = e.strip()
                if e.isdigit():
                    username = useridToUsername(e)
                    if username:
                        result.append('{}:{}'.format(e, username))
                        file.write('{}:{}\n'.format(e, username))
                    else:
                        print('[-] "{}" Not Found!\n'.format(e))
                else:
                    userid = usernameToUserId(e)
                    if userid:
                        result.append('{}:{}'.format(userid, e))
                        file.write('{}:{}\n'.format(userid, e))
                    else:
                        print('[-] "{}" Not Found!\n'.format(e))

        print('[++] Result saved as result.txt')
        return 0

    if args.id is not None:
        username = useridToUsername(args.id)
        if not username:
            print('[-] UserID does not exist')
        else:
            print('[+] Username: {}'.format(username))

    if args.username is not None:
        userid = usernameToUserId(args.username)
        if not userid:
            print('[-] Username does not exist')
        else:
            print('[+] UserID: {}'.format(userid))
    if args.id is None and args.username is None:
        parser.print_help()


if __name__ == '__main__':
    main()
