#!/usr/bin/python
# python 2.7
#_*_ coding: utf-8 _*_

"""
@file			tumblr-tools.py
@author			Simon Burkhardt - simonmartin.ch
@date			2017-07-02
@version		1.0
@brief			
@details		-
"""

"""
usage:

$ tumblr-tools -i [dir] 
				-o [dir] 
				--filter-tag [tag] 
							  linux
							  "linux|art"
							  "passing cloud|artwork"
				--filter-content [keyword]
				--filter-type [type]
				--download-images

				--download-likes [blog]
				--download-posts [blog]

output:
[post-id].json 							      https://tmblr.co/[short-url] 	  [type] 	[query match] 			[title text]
blog/likes/53016737529.json     	https://tmblr.co/ZTEnmxnO2pRv	  text	  linux               everyone's first vi session

"""

# ===== COLORS =====
# https://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
class bcolors:
	HEADER = '\033[95m'		# purple
	OKBLUE = '\033[94m'		# blue
	OKGREEN = '\033[92m'	# green
	WARNING = '\033[93m'	# yellow
	FAIL = '\033[91m'		# red
	ENDC = '\033[0m'		# white / reset
	BOLD = '\033[1m'		# bold
	UNDERLINE = '\033[4m'	# underline

try:
	import sys 								# args
	import optparse 						# argument parser
	import os 								# files, directories
	import json 							# parsing post files
	import fileinput						# read from sys.stdin
	import unicodedata						# ascii formating for sys.stdout
	import urllib 							# downloading images
	import urllib2 							# downloading posts / likes
	import time 							# api request delays
except Exception, ex:
	print("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] Error: " + str(ex))
	exit(-1)

# hardcoded api-key - not for release - option to specify own key with --api-key [key] 
api_key_fix = ""

# ===== ARGUMENTS =====
parser = optparse.OptionParser('tumblr-tools')
parser.add_option('-i', '--input-dir', 						dest='indir', 	type='string', 	help='specify the source directory containing the [post-id].json files')
parser.add_option('-o', '--optut-dir',  					dest='outdir', 	type='string', 	help='[optional] specify the directory to output the filtered [post-id].json files')
parser.add_option('-g', '--tag', '--filter-tags',  			dest='tag', 	type='string', 	help='filter for certain tags')
parser.add_option('-c', '--content', '--filter-content',  	dest='con', 	type='string', 	help='filter for certain keywords or sentences within the post')
parser.add_option('-t', '--type', '--filter-type',  		dest='typ', 	type='string', 	help='filter only for a certain type of post (text, quote, link, answer, video, audio, photo, chat)')
parser.add_option('-u', '--user', '--filter-user',  		dest='usr', 	type='string', 	help='filter only for posts from a certain user')
parser.add_option('-v', '--verbose', action="store_true",	dest='verb', 					help='[optional] verbose output - required for piping the output into tumblr-tools again')
parser.add_option('--get-images', 	action="store_true",	dest='dl_img', 					help='[optional] download the images from posts of the type photo')
parser.add_option('--download-posts', action="store_true",	dest='dl_post', 					help='download the posts of a blog')
parser.add_option('--download-likes', action="store_true",	dest='dl_like', 					help='download the likes of a blog')
parser.add_option('-b', '--blog',							dest='blog',	type='string', 	help='blogname or url to download likes / posts from')
parser.add_option('--api-key', 								dest='api_key',	type='string', 	help='[optional] api-key required to download posts')

(opts, args) = parser.parse_args()

if ( opts.tag is None and opts.typ is None and opts.con is None and opts.typ is None and not opts.dl_img and not opts.dl_post and not opts.dl_like):
	parser.print_help()	
	exit(0)

# https://stackoverflow.com/questions/7113032/overloaded-functions-in-python
def filter_tag(blog, filename=None):
	if ( filename is None):
		filename = blog.rsplit("/", 1)[1]
		blog = blog.split(filename)[0]
	if (".json" in filename):
		with open(blog + filename) as jfile:
			json_re = json.load(jfile)
			tags = str(opts.tag.lower()).split("|")
			found = ""
			for i in range( len(json_re["tags"]) ):			# tags to search in
				for query in tags :							# tags to search for
					if ( query == json_re["tags"][i].lower() ):
						found += query + " | "
			if (len(found) > 0):
				printpost(blog, json_re, found)

def filter_type(blog, filename=None):
	if ( filename is None):
		filename = blog.rsplit("/", 1)[1]
		blog = blog.split(filename)[0]
	if (".json" in filename):
		with open(blog + filename) as jfile:
			json_re = json.load(jfile)
			if ( opts.typ.lower() == json_re["type"].lower() ):
				printpost(blog, json_re, "")

def filter_content(blog, filename=None):
	if ( filename is None):
		filename = blog.rsplit("/", 1)[1]
		blog = blog.split(filename)[0]
	if (".json" in filename):
		with open(blog + filename) as jfile:
			json_re = json.load(jfile)
			tags = str(opts.con.lower()).split("|")
			found = ""
			if ("trail" in json_re):
				for query in tags:					# words to search for
					for i in range( len(json_re["trail"]) ):
						if (unicode(query, "unicode-escape").lower() in json_re["trail"][i]["content_raw"].lower()):
							found += "\"" + query + "\" | "
							i = len(json_re["trail"])+10
			if ("body" in json_re):
				for query in tags:					# words to search for 
					if (unicode(query, "unicode-escape").lower() in json_re["body"].lower()):
						found += "\"" + query + "\" | "
			if ("text" in json_re):
				for query in tags:					# words to search for 
					if (unicode(query, "unicode-escape").lower() in json_re["text"].lower()):
						found += "\"" + query + "\" | "
			if (len(found) > 0):
				printpost(blog, json_re, found)

def filter_user(blog, filename=None):
	if ( filename is None):
		filename = blog.rsplit("/", 1)[1]
		blog = blog.split(filename)[0]
	if (".json" in filename):
		with open(blog + filename) as jfile:
			json_re = json.load(jfile)
			if ( opts.usr.lower() in json_re["blog_name"].lower() ):
				printpost(blog, json_re, json_re["blog_name"])

def download_images(blog, filename=None):
	if ( filename is None):
		filename = blog.rsplit("/", 1)[1]
		blog = blog.split(filename)[0]
	if (".json" in filename):
		with open(blog + filename) as jfile:
			json_re = json.load(jfile)
			if ( "photo" in json_re["type"].lower() ):
				if ( opts.outdir is not None ):
					photo_path = opts.outdir
					if ( len(json_re["photos"]) > 1 ):		# create a post subdir if the posts contains multiple photos
						photo_path += "/" + str(json_re["id"])
					mkdir_p(photo_path)
				else:
					print("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] error: you need to specify an output directory")
					exit(0)
				print("[" + bcolors.OKGREEN + "+" + bcolors.ENDC + "] info: downloading " + str(len(json_re["photos"])) + " photos from post: " + filename)
				for p in range(len(json_re["photos"])):
					photo_url = json_re["photos"][p]["original_size"]["url"]
					photo_name = photo_path + "/" + str(json_re["id"]) + "_" + photo_url.rsplit("/", 1)[1]
					photo_path = photo_path.replace("//", "/")
					urllib.urlretrieve(photo_url, filename=photo_name)

def download_posts(blogname, typus):
	# check api-key
	if ( opts.api_key is not None ):
		api_key = opts.api_key
	elif ( len(api_key_fix) < 10):
		print("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] error: no api-key found, please specify one using the --api-key [key] option")
		exit(0)
	else:
		api_key = api_key_fix
	# test api-key by tumblr:
	# https://api.tumblr.com/v2/blog/BLOGNAME-HERE.tumblr.com/info?api_key=fuiKNFp9vQFvjLNvx4sUwti4Yb5yGutBN4Xh10LXZhhRKjWlV4
	# find out how many posts have to be downloaded
	url = "https://api.tumblr.com/v2/blog/" + blogname + ".tumblr.com/info?api_key=" + api_key
	# print url
	try:
		response = urllib2.urlopen(url).read()
	except urllib2.HTTPError, ex:
		print ("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] error: " + str(ex))
		exit(0)
	except Exception, ex:
		print ("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] error: trouble requesting information about the blog \"" + blogname + "\"" )
		exit(-1)
	json_re = json.loads(response)
	if ( typus in json_re["response"]["blog"] ):
		postcount = json_re["response"]["blog"][typus]		# blog/likes or blog/posts
	else:
		print ("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] error: can't fetch \"" + typus + "\" from \"" + blogname + "\" (not publicly available?)" )
		exit(-1)
	if ( opts.outdir is not None ):
		blog_path = opts.outdir + "/" + typus
		mkdir_p(blog_path)
	else:
		print("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] error: you need to specify an output directory")
		exit(0)

	# REQUESTS & TIMING (API request limitations)
	# https://www.tumblr.com/oauth/apps
	# @Todo: create optparse options to wrap the following variables for a more specific download of posts
	max_req_h = 250				# maximum of  200 (default) requests per hour
	max_req_d = 5000			# maximum of 5000 (default) requests per day
	post_type = ""				# specific posts, eg. photo, text - leave blank "" for all posts
	post_offset = 0				# specify at which post to start downloading
	n_requests = postcount / 20
	if(n_requests*20 < postcount):
		n_requests += 1
	print ("[" + bcolors.OKGREEN + "+" + bcolors.ENDC + "] info: downloading " + str(postcount) + " posts, generating: " + str(n_requests) + " requests")
	if (n_requests > 250):
		t_min_h = 60*60 / max_req_h
		t_min_d = 60*60*24 / max_req_d
		t_delay = 0
		if ( t_min_h > t_min_d ):
			t_delay = t_min_h
		else:
			t_delay = t_min_d
		t_delay = t_delay + 1	# add 1 to make up for the lost floating point numbers
		t_total = n_requests * t_delay / 60
		print ("[" + bcolors.OKGREEN + "+" + bcolors.ENDC + "] info: estimated download time: " + str(t_total / 60) + " hours " + str(t_total - ((t_total / 60)*60)) + " minutes." )
		print ("[" + bcolors.OKGREEN + "+" + bcolors.ENDC + "] info: delay setting: " + str(t_delay) + "s" )
	else:
		t_delay = 0
		print ("[" + bcolors.OKGREEN + "+" + bcolors.ENDC + "] info: api limitations are not reached, downloading without delay")

	# DOWNLOADING
	for i in range(n_requests):
		fst = (i * 20) + post_offset
		uri = "https://api.tumblr.com/v2/blog/" + blogname + ".tumblr.com/" + typus + "/" + post_type + "?api_key=" + api_key + "&offset=" + str(fst)
		if (fst+20 > postcount):
			print ("[" + bcolors.OKGREEN + "+" + bcolors.ENDC + "] downloading: posts " + str(fst) + " - " + str(postcount) )
		else:
			print ("[" + bcolors.OKGREEN + "+" + bcolors.ENDC + "] downloading: posts " + str(fst) + " - " + str(fst+20) )

		response = urllib2.urlopen(uri).read()
		json_re = json.loads(response)

		if ("likes" in typus) :
			json_key = "liked_posts"
		else:
			json_key = "posts"

		for i in range(len(json_re["response"][json_key])) :
			filename = str(json_re["response"][json_key][i]["id"]) + ".json"
			# print ( filename )
			with open(blog_path + "/" + filename, "w") as outfile :
				json.dump(json_re["response"][json_key][i], outfile)

		time.sleep(t_delay) # wait between requests, so that the api limitations are met

def trim_text(text, limit):
	if len(text) > limit:
		newLen = limit -3
		text = text[:newLen] + "..."
	return text

def printpost(name, post, line):
	if ( "|" in line ):
		line = line[:(len(line)-3)]			# remove the " | "
	line = trim_text(line, 16) + "                "[:16]

	if ( "title" in post and post["title"] is not None ):
		title = post["title"]
	else:
		urlparts = post["post_url"].split("/")
		title = urlparts[len(urlparts)-1].replace("-", " ")
		if ( title.isnumeric() ):
			title = ""
	title = trim_text(title, 32)
	filnam = str(post["id"]) + ".json     "[:17]		# equal size of filnames

	if ( opts.verb ):	# verbose
		formated_line = ( name + filnam + "\t" + post["short_url"] + "\t" + post["type"] + "\t" + line + "\t" + title + "\n")
	else:
		formated_line = (post["short_url"] + "\t" + title + "\n")
	# https://www.quora.com/How-do-I-get-around-the-Python-error-UnicodeEncodeError-ascii-codec-cant-encode-character-when-using-a-Python-script-on-the-command-line
	formated_line = unicodedata.normalize('NFKD', formated_line).encode('ascii','ignore')
	sys.stdout.write(formated_line)

# MKDIR function
def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc:  # Python >2.5
		if ( os.path.isdir(path) ):
			pass
		else:
			raise

# main code
try:	# except Keyboard interrupt
	# FILTER POSTS
	task = 0
	if ( opts.tag is not None ):
		task += 1
	if ( opts.typ is not None):
		task += 2
	if ( opts.con is not None ):
		task += 4
	if ( opts.usr is not None ):
		task += 8
	if ( opts.dl_img ):
		task += 16
	if ( opts.dl_post or opts.dl_like ):
		task += 32

	if ( task > 0 ):
		# check where to get the input files from
		if ( opts.indir is not None ):
			if (not os.path.isdir(opts.indir) ):
				print("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] error: could not find the folder " + str(opts.indir))
				exit(0)
			else:
				blogname = (str(opts.indir) + "/").replace("//", "/")		# make sure blogname ends with "/"
				if not ( blogname.endswith("/") ):
					blogname += "/"
				# FILTER TAGS
				if ( task is 1 ):
					for f in os.listdir(blogname):
						filter_tag(blogname, f)
				# FILTER TYPE
				elif ( task is 2 ):
					for f in os.listdir(opts.indir):
						filter_type(blogname, f)
				# FILTER CONTENT
				elif ( task is 4 ):
					for f in os.listdir(opts.indir):
						filter_content(blogname, f)
				# FILTER USER
				elif ( task is 8 ):
					for f in os.listdir(opts.indir):
						filter_user(blogname, f)
				# DOWNLOAD IMAGES
				elif ( task is 16 ):
					for f in os.listdir(opts.indir):
						download_images(blogname, f)
				else:
					print("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] error: can't filter for multiple queries at the same time")
					exit(0)
		elif ( task is 32 ):
			# DOWNLOAD BLOG
			if ( opts.blog is None ):
				print("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] error: no blogname specified, use the --blog [blogname] option")
				exit(0)
			bl_name = opts.blog.split(".tumblr.com")[0].replace("http://", "").replace("https://", "").replace("www.", "")
			if ( opts.dl_like ):
				bl_dl = "likes"
			elif ( opts.dl_post ):
				bl_dl = "posts"
			download_posts(bl_name, bl_dl)
		# FILTER STDIN			
		else:
			# https://stackoverflow.com/questions/1450393/how-do-you-read-from-stdin-in-python#1454400
			# check if stdin contains data
			# https://stackoverflow.com/questions/3762881/how-do-i-check-if-stdin-has-some-data#17735803
			if sys.stdin.isatty():
				print ("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] error: piped input is empty")
				exit(0)
			# FILTER TAGS
			if ( task is 1 ):
				for l in sys.stdin:
					post_link = l.split(" ")[0]
					if (".json" in post_link):
						filter_tag(post_link)
					else:
						print ("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] error: piped input does not contain valid posts")
						print ("encountered at:\t" + post_link)
						exit(0)
			# FILTER TYPE
			elif ( task is 2 ):
				for l in sys.stdin:
					post_link = l.split(" ")[0]
					if (".json" in post_link):
						filter_type(post_link)
					else:
						print ("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] error: piped input does not contain valid posts")
						print ("encountered at:\t" + post_link)
						exit(0)
			# FILTER CONTENT
			elif ( task is 4 ):
				for l in sys.stdin:
					post_link = l.split(" ")[0]
					if (".json" in post_link):
						filter_content(post_link)
					else:
						print ("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] error: piped input does not contain valid posts")
						print ("encountered at:\t" + post_link)
						exit(0)
			# FILTER USER
			elif ( task is 8 ):
				for l in sys.stdin:
					post_link = l.split(" ")[0]
					if (".json" in post_link):
						filter_user(post_link)
					else:
						print ("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] Error: piped input does not contain valid posts")
						print ("encountered at:\t" + post_link)
						exit(0)
			# GET PHOTOS
			elif ( task is 16 ):
				for l in sys.stdin:
					post_link = l.split(" ")[0]
					if (".json" in post_link):
						download_images(post_link)
					else:
						print ("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] Error: piped input does not contain valid posts")
						print ("encountered at:\t" + post_link)
						exit(0)
			else:
				print("[" + bcolors.FAIL + "-" + bcolors.ENDC + "] Error: can't filter for multiple queries at the same time")
				exit(0)

# enables abortion of the program by CTRL + C
except KeyboardInterrupt:
	print("")
	exit()
