from lib import pukibot

# PukiWikiのURL
URL = "https://wikichree.com/TrialWiki/"

bot = pukibot.PukiBot(URL)

#bot.savePage("aaa", "aaaaaaa")
print(bot.getLastModifiedTime("aaa"))

#print(bot.getPageSource("aaaa"))