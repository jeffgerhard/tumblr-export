import requests
import dotenv
from bs4 import BeautifulSoup

import os
import sys
import json
import urllib
from dateutil.parser import parse


class ApiError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

dotenv_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

API_KEY = os.environ['TUMBLR_API_KEY']
BLOG_IDENTIFIER = os.environ['TUMBLR_BLOG_IDENTIFIER']
REQUEST_RANGE = 20


def get_request(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise ApiError('GET {} {}'.format(url, resp.status_code))

    return resp


def get_post_count():
    resp = get_request('https://api.tumblr.com/v2/blog/{}/posts?api_key={}'.format(BLOG_IDENTIFIER, API_KEY))
    json_resp = resp.json()['response']
    total_posts = json_resp['total_posts']
    print('{} posts'.format(total_posts), file=sys.stderr)
    return total_posts


def get_posts(offset):
    print('Fetching posts {} to {}'.format(offset, offset + REQUEST_RANGE), file=sys.stderr)
    posts_url = 'https://api.tumblr.com/v2/blog/{}/posts?api_key={}&offset={}'.format(BLOG_IDENTIFIER, API_KEY, offset)
    resp = get_request(posts_url)
    json_resp = resp.json()['response']
    return json_resp['posts']

# Get all the posts.
post_count = get_post_count()
offset = 0
posts = []
while offset < post_count:
    posts.extend(get_posts(offset))
    offset += REQUEST_RANGE

posts.reverse()

# Dump the posts and images.
BLOG = posts[0]['blog_name']
OUTPUT_DIR = sys.argv[1] if len(sys.argv) > 1 else BLOG

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(os.path.join(OUTPUT_DIR, 'posts.json'), 'w', encoding='utf-8') as fh:
    fh.write(json.dumps(posts, indent=4))

for post in posts:
    d = parse(post['date'])
    fold = str(d.date()) + ' [' + post['type'] + '] ' + post['slug']
    post_dir = os.path.join(OUTPUT_DIR, fold.strip())
    os.makedirs(post_dir, exist_ok=True)
    with open(os.path.join(post_dir, '{}.json'.format(post['slug'])), 'w') as text_file:
        print(json.dumps(post, indent=4), file=text_file)

    if 'body' in post:
        soup = BeautifulSoup(post['body'], 'html.parser')
        imgs = soup.find_all('img')
        for idx, img in enumerate(imgs):
            img_url = img['src']
            numb = ''
            if idx > 0:
                numb = '_' + str(idx)
            filename = post['slug'] + numb + os.path.splitext(os.path.basename(urllib.parse.urlparse(img_url).path))[1]
            print('fetching {}...'.format(filename), file=sys.stderr)
            urllib.request.urlretrieve(img_url, os.path.join(post_dir, filename))
    if 'photos' in post:
        for idy, photo in enumerate(post['photos']):
            for idx, x in enumerate(photo):
                if x == 'original_size':
                    img_url = post['photos'][idy]['original_size']['url']
                    filename = post['slug'] + os.path.splitext(os.path.basename(urllib.parse.urlparse(img_url).path))[1]
                    urllib.request.urlretrieve(img_url, os.path.join(post_dir, filename))
                if x == 'alt_sizes':
                    os.makedirs(os.path.join(post_dir, 'alt_sizes'), exist_ok=True)
                    for alts in post['photos'][idy]['alt_sizes']:
                        img_url = alts['url']
                        filename = os.path.basename(urllib.parse.urlparse(img_url).path)
                        urllib.request.urlretrieve(img_url, os.path.join(post_dir, 'alt_sizes', filename))
