tumblr-export.py will dump all of the posts (and images) from a Tumblr blog into JSON files in a directory.

Forked from [ottumm](https://github.com/ottumm/tumblr-export)'s version for my own personal use case and to clarify some of the image downloading features.

# Installation
```
pip3 install -r requirements.txt
```

# Usage
Set the following environment variables (or use a dotenv file):
```
TUMBLR_API_KEY=api key from api.tumblr.com
TUMBLR_BLOG_IDENTIFIER=example.tumblr.com
```
Then run:
```shell
python3 tumblr-export.py [OUTPUT_DIR]
```

If no OUTPUT_DIR is specified, JSON files will be created in a directory named for the tumblr.

# Output Format
One directory per post, with a JSON file and any post images contained in the directory. Directories are named with the post date, post type, and post slug (if any). Each post file is in the JSON format defined at https://www.tumblr.com/docs/en/api/v2#posts.
