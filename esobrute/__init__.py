from multiprocessing import Process
import os
import json
import zlib
import binascii
import re

from termcolor import colored, cprint
import requests
import click

def enhex(text):
  return binascii.hexlify(text)

def unhex(text):
  return binascii.unhexlify(text)

def get_html():
  return requests.get(base_url).content

def get_js(html):
  js_url = base_url+re.search('<script src=\"(.*frontend.js)\"', html).group().split('"')[1]
  return requests.get(js_url).content

def get_run_url(js_file):
  return base_url+re.search('var runURL = \"(.*)\";', js_file).group().split('"')[1]

def get_lang(js_file):
  url = base_url + re.search('languageFileRequest\.open\(\"GET\", \"(.*)\"', js_file).group().split('"')[3]
  return map(lambda x: x.encode('ascii'), json.loads(requests.get(url).content).keys())

def run_code(code, lang):

  data = '566C616E67003100'
  data += enhex(lang)
  data += '00462E636F64652E74696F00'
  data += enhex(str(len(code)))
  data += '00'
  data += enhex(code)
  data += '462E696E7075742E74696F003000566172677300300052'
  data = unhex(data)
  
  comp = zlib.compressobj(9, zlib.DEFLATED, -15)
  data = comp.compress(data)
  data += comp.flush()

  token = enhex(os.urandom(16))

  res = requests.post(run_url+'/'+token, data=data).content
  res = res[10:]
  res = zlib.decompress(res, -15)

  return res[16:].split(res[:16])

def run_task(code, langs):
  try:
    for e in langs:
      output = run_code(code, e)[0]
      output = output.replace('\n', '.')
      if LENGTH_MAX >= 0 and len(output) > LENGTH_MAX:
        output = output[:100]+'...'
      if len(output) > 0 and enhex(OUTPUT_FILTER) in enhex(output):
        cprint('{}: {}'.format(e, output), 'green')
      else:
        cprint('{}: XXX'.format(e), 'white', attrs=['dark'])
  except KeyboardInterrupt:
    pass


THREAD_COUNT = 20
LENGTH_MAX = 100
OUTPUT_FILTER = ''

base_url = 'https://tio.run'
run_url = ''


@click.command()
@click.argument('file', type=click.File('rb'), nargs=1)
@click.option('--thread', '-t', default=20, help='Number of threads')
@click.option('--plain', '-p', is_flag=True)
@click.option('--list-lang', '-ls', is_flag=True)
@click.option('--lang', '-l', default='', help='Selected language')
@click.option('--lang-filter', '-lf', default='', help='filter languages')
@click.option('--output-filter', '-of', default='', help='filter output')
def main(file, thread, plain, list_lang, lang, lang_filter, output_filter):
  global run_url, THREAD_COUNT, LENGTH_MAX, OUTPUT_FILTER, cprint
  
  if plain:
    def p(text, *args, **kwargs):
      print text
    cprint = p

  cprint('starting esobrute', 'blue')
  code = file.read()

  THREAD_COUNT = thread
  OUTPUT_FILTER = output_filter
  

  if run_url == '':
    html = get_html()
    js_file = get_js(html)
    run_url = get_run_url(js_file)
    print 'got run_url'

  if lang == '':
    languages = get_lang(js_file)
    print 'got languages'
  else:
    languages = lang.split(',')

  if lang_filter != '':
    temp = []
    for each in languages:
      if lang_filter in each:
        temp.append(each)
    languages = temp

  cprint('Languages:','blue')
  for each in languages:
    cprint('\t'+each, 'blue')

  if list_lang:
    return

  if len(languages) == 1:
    LENGTH_MAX = -1

  THREAD_COUNT = min(len(languages), THREAD_COUNT)

  threads = []
  step = len(languages)//THREAD_COUNT
  for i in range(THREAD_COUNT):
    task = []
    if i+1 < THREAD_COUNT:
      tasks = languages[i*step:(i+1)*step]
    else:
      tasks = languages[i*step:]
    t = Process(name='thread{}'.format(i+1), target=run_task, args=(code, tasks,))
    # t = threading.Thread(name='thread{}'.format(i+1), target=run_task, args=(code, tasks,))

    t.start()
    threads.append(t)
    print 'thread {} started'.format(i+1)

  for each in threads:
    each.join()

if __name__ == '__main__':
  main()
