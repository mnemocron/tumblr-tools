## Tumblr Tools

---

[![volkswagen status](https://auchenberg.github.io/volkswagen/volkswargen_ci.svg?v=1)](https://github.com/auchenberg/volkswagen)

This Script uses the Tumblr API to download `likes` and `posts` form any blog to your local machine in the `json` format. You can also filter the downloaded posts for `tags`, `users`, `content` (keywords) and `post-type`.

**Before use:**

You need to register an API key on Tumblr and write it into the script.

---

### Usage

Download all posts from `my-blog.tumblr.com`:

```bash
python2 tumblr-tools.py --download-posts -b my-blog -o my-blog 
```

afterwards, download all images that are inside of the just downloaded posts:

```bash
python2 tumblr-tools.py --get-images -i my-blog/posts/ -o my-blog
```

Creates the following floder structure:

```
tumblr-tools
├── my-blog/
|   ├── posts/
|   |   ├── 190015323997.json
|   |   ├── 190015323998.json
|   |   ├── .
|   |   ├── .
|   |   └── .
|   └── iamges/
|       ├── 190015323997
|       |   ├── 190015323997_tumblr_ohuma5Hsu81un1bxho4_400.jpg
|       |   └── 190015323997_tumblr_ohuma5Hsu81un1bxho3_400.jpg
|       ├── 190015323998_tumblr_o5kxnfxxHY1s0jodno1_540.jpg
|       ├── .
|       ├── .
|       └── .
```

Search for keywords in posts:

```bash
python2 tumblr-tools.py -i my-blog/posts/ --content "love"
https://tmblr.co/ZP8L3f██████a  mujischolar concept me living...
https://tmblr.co/ZP8L3f██████S  vicioussuggestion i literally...
https://tmblr.co/ZP8L3f██████A  2017 the year i learn to forg...
https://tmblr.co/ZP8L3f██████a  sunnyxdraco m1sc1efmanaged
...
```

Pass `--verbose` to pipe the results back into the script to then filter again:

```bash
python2 tumblr-tools.py -i my-blog/posts/ --content "love" --verbose | python2 tumblr-tools.py --type "photo"
```

---

### License

[WTFPL](http://www.wtfpl.net/)

Provided as is - do whatever you want
