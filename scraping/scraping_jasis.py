import urllib
from bs4 import BeautifulSoup as bs
import os
import re
import csv
from time import sleep
import pandas as pd

url = "https://www.jasis.jp/exhibitors/jp/"

html = urllib.request.urlopen(url)
soup = bs(html, "html.parser")

a = soup.find_all("a")
pattern = re.compile("./exhibitor")

df = pd.DataFrame(columns=["Company", "URL"])

for href_ in a:
	text = href_.get_text()
	href = href_.get("href")
	if href != None and pattern.match(href):
		href = os.path.join(url, href)
		html2 = urllib.request.urlopen(href)
		soup2 = bs(html2, "html.parser")
		a2 = soup2.find_all("div", attrs={"class":"web_koma tR"})
		url3 = ""
		for i in a2:
			url2 = i.get("href")
			url2 = i.find("a").get("href")
			url3 = url2
		sleep(0.5)

		print(text, url3)
		tmp = pd.Series([text, url3], index=df.columns)
		df = df.append(tmp, ignore_index=True)

print(df)
df.to_csv("exhibition_jasis.csv")