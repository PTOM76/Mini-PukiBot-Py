from urllib import request
import urllib.parse
import re
import hashlib

class PukiBot:
	
	def __init__(this, url = None):
		this.setUrl(url)
		this.setUserAgent("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0")
	
	# ユーザーエージェントを設定
	def setUserAgent(this, agent):
		this.userAgent = agent
	
	# ユーザーエージェントを取得
	def getUserAgent(this):
		return this.userAgent
	
	# URLを設定
	def setUrl(this, url):
		this.url = url
	
	# URLを取得
	def getUrl(this):
		return this.url
	
	# ページのインスタンスを作成し、ソースのレスポンスをsource変数へ保存し、インスタンスを返す
	def createPageInstance(this, pagename):
		page = Page(this, pagename)
		page.receiveSource()
		return page
	
	# ページソースを取得
	def getPage(this, pagename):
		page = Page(this, pagename)
		return page.getSource()
	
	# ページの存在チェック
	def existPage(this, pagename):
		page = Page(this, pagename)
		return page.isExist()
	
	# ページを編集して保存 (存在しない場合は作成されるはず)
	def savePage(this, pagename, source, notimestamp = False):
		page = Page(this, pagename)
		return page.save(source)
	
	# ページを削除
	def deletePage(this, pagename):
		return this.savePage(pagename, "")
	
	# 最終更新日時を取得 (形式: xxxx-xx-xxTxx:xx:xx+xx:xx) [1.5.1～]
	def getLastModifiedTime(this, pagename):
		return getLastModifiedTime(this.getPage(pagename))
	
	# 編集者名を取得 [1.5.1～]
	def getAuthorName(this, pagename):
		return getAuthorName(this.getPage(pagename))
	
	# 編集者のフルネームを取得 [1.5.1～]
	def getAuthorFullName(this, pagename):
		return getAuthorFullName(this.getPage(pagename))

class Page:
	
	# bot: PukiBotのインスタンス, pagename: ページ名
	def __init__(this, bot, pagename):
		if type(bot) != PukiBot:
			raise TypeError("タイプが不正です(正しいタイプ: PukiBot)")
		this.bot = bot
		this.name = pagename
		this.source = ""
		this.html = ""
	
	# PukiBotのインスタンスを取得
	def getBot(this):
		return this.bot
	
	# ページを保存 (※返り値はアクセスできなかった場合にFalseとなります)
	def save(this, source, notimestamp = False):
		try:
			url = this.bot.getUrl()
			header = {
				"User-Agent": this.bot.getUserAgent(),
				"content-type": "application/x-www-form-urlencoded"
			}
			if notimestamp:
				notimestamp = "on"
			else:
				notimestamp = "off"
			digest = hashlib.md5(this.getSource().encode("utf-8")).hexdigest() if this.isExist() else "d41d8cd98f00b204e9800998ecf8427e"
			data = urllib.parse.urlencode({
				"encode_hint": "ぷ",
				"cmd": "edit",
				"digest": digest,
				"page": this.name,
				"write": "ページの更新",
				"msg": source,
				"client": "bot",
				"notimestamp": notimestamp
			})
			req = urllib.request.Request(url, data=data.encode(), headers=header, method='POST')
			res = request.urlopen(req)
			content = res.read()
			res.close()
			html = content.decode()
			return True
		except:
			return False
	
	# sourceプラグインが存在しない場合の手段
	def receiveSourceFromDiff(this):
		try:
			url = this.bot.getUrl() + "?cmd=diff&page=" + urllib.parse.quote(this.name) + "&client=bot"
			header = {
				"User-Agent": this.bot.getUserAgent()
			}
			req = urllib.request.Request(url, headers=header)
			res = request.urlopen(req)
			content = res.read()
			res.close()
			html = content.decode()
			this.html = html
			try:
				split = re.split('<pre.*?>', html)
				this.source = re.split('</pre>', split[1])[0]
				this.source = re.sub(r'<span .*?class="diff_removed".*?>.*?</span>\n?', "", this.source)
				this.source = re.sub(r'<[^>]*?>', "", this.source)
				this.source = convertSourceFromPreSource(this.source)
				return True
			except:
				this.source = ""
				return False
		except:
			return False
	
	# ソースをページから取得してsource変数に保存 (返り値: boolean)
	def receiveSource(this):
		try:
			url = this.bot.getUrl() + "?cmd=source&page=" + urllib.parse.quote(this.name) + "&client=bot"
			header = {
				"User-Agent": this.bot.getUserAgent()
			}
			req = urllib.request.Request(url, headers=header)
			res = request.urlopen(req)
			content = res.read()
			res.close()
			html = content.decode()
			this.html = html
			try:
				split = re.split('<pre id="source".*?>', html)
				this.source = re.split('</pre>', split[1])[0]
				this.source = re.sub(r'<[^>]*?>', "", this.source)
				this.source = convertSourceFromPreSource(this.source)
				return True
			except:
				# 差分から取り出す
				if (this.receiveSourceFromDiff()):
					return True
				print("ソースが見つかりませんでした")
				this.source = ""
				return False
		except:
			# 差分から取り出す
			if (this.receiveSourceFromDiff()):
				return True
			print("ページが見つかりませんでした")
			return False
	
	# HTMLのソースを取得
	def getHTMLSource(this):
		return this.html
	
	# ページの存在確認 (boolean)
	def isExist(this):
		try:
			url = this.bot.getUrl() + "?" + urllib.parse.quote(this.name) + "&client=bot"
			header = {
				"User-Agent": this.bot.getUserAgent()
			}
			req = urllib.request.Request(url, headers=header)
			res = request.urlopen(req)
			content = res.read()
			res.close()
			html = content.decode()
			this.html = html
			
			if re.search('<textarea name="msg".*?>.*?</textarea>', html):
				return False
			if re.search('<h3>Runtime error</h3>\n<strong>Error message : PKWK_READONLY prohibits editing</strong>', html):
				return False
			
			return True
		except:
			print("ページが見つかりませんでした")
			return False
	
	# ページのソースを取得 (sourceプラグインが除去されている場合、使えません)
	def getSource(this):
		if not this.source:
			this.receiveSource()
		return this.source
	
def convertSourceFromPreSource(str):
	str = str.replace("&amp;", "&")
	str = str.replace("&lt;", "<")
	str = str.replace("&gt;", ">")
	str = str.replace("&quot;", "\"")
	return str

# ソースコードの#author(...)から最終更新日時を取り出します (形式: xxxx-xx-xxTxx:xx:xx+xx:xx)
def getLastModifiedTime(source):
	m = re.search(r"^#author\(\"(.*?)(?:;.*?)?\",", source)
	return m.group(1)

# ソースコードの#author(...)からユーザーネームを取り出します
def getAuthorName(source):
	m = re.search(r"^#author\(\".*?\",\"(.*?)\"", source)
	return m.group(1)

# ソースコードの#author(...)からフルネームを取り出します
def getAuthorFullName(source):
	m = re.search(r"^#author\(\".*?\",\".*?\",\"(.*?)\"", source)
	return m.group(1)