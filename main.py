
# (c) 2020 Kazuki KOHZUKI

import configparser as cp
import json
import re
import requests
from html import unescape
from unicodedata import east_asian_width

HTML_TPL = '''
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>点数一覧</title>
    <style type="text/css">*{font-size:16px}@media screen and (min-width: 600px) and (max-width: 960px){body{width:550px}body main{width:470px}}@media screen and (min-width: 960px) and (max-width: 1280px){body{width:900px}body main{width:820px}}@media screen and (min-width: 1280px){body{width:980px}body main{width:900px}}*{font-family:'Hiragino Kaku Gothic ProN', YuGothicM, YuGothic, sans-serif}@font-face{font-family:YuGothicM;font-weight:normal;src:local("YuGothic-Medium"),local("Yu Gothic Medium"),local("YuGothic-Regular")}@font-face{font-family:YuGothicM;font-weight:bold;src:local("YoGothic-Bold"),local("Yu Gothic")}body{margin:20px auto;background-color:#fff}h1{font-size:32px;margin:0 auto}h2{font-size:24px;margin-left:-10px;margin-right:-10px;margin-top:25px;padding-left:10px;padding-right:20px;border-bottom:1.2px solid #BCBCBC}table{width:100%;border-spacing:0;margin-right:10px;border-bottom:2px solid #d9d9d9}.thead{background-color:#d9d9d9}.thead__title{width:200px}.thead__score{width:80px}.tbody tr:nth-child(even){background:#e8e7e7}.tbody__title{width:200px}.tbody__score{width:80px;text-align:center}</style>
  </head>
  <body>
    <main>
      <h1>課題等点数一覧</h1>
			<!--LIST-->
    </main>
  </body>
</html>
'''

LOGIN_URL = 'https://cas.ecs.kyoto-u.ac.jp/cas/login?service=https%3A%2F%2Fpanda.ecs.kyoto-u.ac.jp%2Fsakai-login-tool%2Fcontainer'
JSON_URL = 'https://panda.ecs.kyoto-u.ac.jp/direct/gradebook/my.json'
CONFIG_PATH = './credential.ini'

def get_data(username, password):
	session = requests.session()
	res = session.get(LOGIN_URL)
	lt = re.search(r'<input type="hidden" name="lt" value="(.+?)".*>', res.text).group(1)

	login_info = {
		'username': username,
		'password': password,
		'warn': 'true',
		'lt': lt,
		'execution': 'e1s1',
		'_eventId': 'submit'
	}

	res = session.post(LOGIN_URL, data=login_info)
	res = session.get(JSON_URL)
	if res.status_code != requests.codes.ok:
		print('ログインに失敗しました。')
		return
	json_str = res.text
	return json.loads(json_str)['gradebook_collection']

def ealen(s):
	return sum(1 for c in s if east_asian_width(c) in 'FWA') + len(s)

def get_assignments(data):
	max_l = 0
	assignments = []
	for assignment in data:
		name = assignment['itemName']
		max_l = max(max_l, ealen(name))
		try:
			score = float(assignment['grade'])
			full = float(assignment['points'])
			grade = f'{score}/{full}'
		except:
			grade = '-'
		assignments.append([name, grade])

	for assignment in assignments:
		assignment[0] += ' ' * (max_l - ealen(assignment[0]))

	return assignments

def output_list(data):
	for lecture in data:
		try:
			lec_name = unescape(lecture['siteName'].split(']')[1])
		except:
			continue

		assignments = get_assignments(lecture['assignments'])
		if len(assignments) == 0:
			continue
		print(f'\n====== {lec_name} ======')

		for assignment in assignments:
			name, grade = assignment
			print(f'{name}    {grade}')

def main():
	config = cp.ConfigParser()
	try:
		config.read(CONFIG_PATH)
		section = config['PandA']
		uname = section['username']
		passwd = section['password']
	except:
		print('ログイン情報の読み取りに失敗しました。credential.iniを確認してください。')
	else:
		scores = get_data(uname, passwd)
		output_list(scores)

if __name__ == '__main__':
	main()
	input('\n(Enterを押して終了)')
