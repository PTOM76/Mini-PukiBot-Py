from lib import pukibot

# PukiWikiのURL
URL = "https://pukiwiki.osdn.jp/"

bot = pukibot.PukiBot(URL)

print(bot.getPage("FrontPage"))