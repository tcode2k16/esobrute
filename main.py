import threading
import os
import json
import zlib
from pwn import *
import re
from bs4 import BeautifulSoup
from termcolor import colored, cprint
import requests

def get_html():
  soup = BeautifulSoup(requests.get(base_url).content, 'html.parser')
  return soup

def get_js(soup):
  for link in soup.find_all('script'):
    if 'frontend' in link.get('src'):
      return requests.get(base_url+link.get('src')).content

def get_run_url(js_file):
  return base_url+re.search('var runURL = \"(.*)\";', js_file).group().split('"')[1]

def get_lang(js_file):
  url = base_url + re.search('languageFileRequest\.open\(\"GET\", \"(.*)\"', js_file).group().split('"')[3]
  return map(lambda x: x.encode('ascii'), json.loads(requests.get(url).content).keys())

def run_code(code, lang):

  data = unhex('566C616E67003100')
  data += lang
  data += unhex('00462E636F64652E74696F00')
  data += str(len(code))
  data += '\x00'
  data += code
  data += unhex('462E696E7075742E74696F003000566172677300300052')
  # print enhex(data)
  # data = open('./data','rb').read()
  
  comp = zlib.compressobj(9, zlib.DEFLATED, -15)
  data = comp.compress(data)
  data += comp.flush()

  token = enhex(os.urandom(16))

  # print base_url+run_url+token
  res = requests.post(run_url+'/'+token, data=data).content
  res = res[10:]
  res = zlib.decompress(res, -15)
  return res[16:].split(res[:16])

  # print data
  # print len(data)

def run_task(code, langs):
  for e in langs:
    # output = run_code(code, e)
    output = run_code(code, e)[0]
    output = output.replace('\n', '.')
    if len(output) > LENGTH_MAX:
      output = output[:100]+'...'
    if len(output) > 0:
      cprint('{}: {}'.format(e, output), 'green')
    else:
      cprint('{}: XXX'.format(e), 'white', attrs=['dark'])

THREAD_COUNT = 20
LENGTH_MAX = 100

base_url = 'https://tio.run'
run_url = ''



if run_url == '':
  html = get_html()
  js_file = get_js(html)
  run_url = get_run_url(js_file)
  print 'got run_url'
  languages = get_lang(js_file)
  print 'got languages'
  # print run_url
  # print languages

# print run_url

# languages = ['javascript-v8']

code = 'echo Hello, World!'
# languages = ['bash']
# for lang in ['unicat']:
#   print run_code(open('./unicat').read(), lang)
threads = []
step = len(languages)//THREAD_COUNT
for i in range(THREAD_COUNT):
  task = []
  if i+1 < THREAD_COUNT:
    tasks = languages[i*step:(i+1)*step]
  else:
    tasks = languages[i*step:]
  t = threading.Thread(name='thread{}'.format(i+1), target=run_task, args=(code, tasks,))
  t.start()
  threads.append(t)
  print 'thread {} started'.format(i+1)

for each in threads:
  each.join()

# data = [31,139,8,0,0,0,0,0,2,3,203,48,10,244,242,205,243,75,49,48,76,241,46,8,75,207,242,72,205,201,201,215,81,8,207,47,202,73,81,228,202,64,147,229,10,74,77,204,81,40,201,204,77,181,82,48,208,51,48,176,84,40,230,10,45,78,45,66,18,50,6,10,5,87,22,235,33,9,153,1,133,156,3,66,21,138,51,18,139,128,66,150,150,122,38,70,10,170,92,174,21,153,37,10,201,249,41,32,85,232,22,1,0,143,163,189,80,151,0,0,0]
# data = map(chr, data)
# data = ''.join(data)[10:]
# print len(data)

# print zlib.decompress(data, -15)