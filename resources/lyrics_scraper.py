'''
Spotify Lyrics Player Project (June 2020)



Dependencies:
sudo apt-get install python3-bs4
pip install bs4
pip install beautifulsoup4
pip install requests

References:
https://www.pluralsight.com/guides/extracting-data-html-beautifulsoup

https://stackoverflow.com/questions/8551230/how-can-i-get-information-from-an-a-href-tag-within-div-tags-with-beautifuls

https://stackoverflow.com/questions/2935658/beautifulsoup-get-the-contents-of-a-specific-table

https://www.stechies.com/compare-lists-python-using-set-cmp-function/
'''

import json
import requests
import webbrowser
from urllib.request import urlopen as uReq
from urllib.parse import urlencode
from bs4 import BeautifulSoup

class ColorCodedLyrics(object):
    song_name = None
    artist_name = None
    search_url = "https://colorcodedlyrics.com/"
    song_url = None
    lyrics = {}

    def __init__(self, song_name, artist_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.song_name = song_name
        self.artist_name = artist_name

#  ========================================================================================== #

    def get_url(self):
        song_url = None
        query = urlencode({"s": f"{self.song_name} {self.artist_name}"})
        lookup_url = f"{self.search_url}?{query}"

        print(lookup_url)
        #webbrowser.open(lookup_url)

        html_content = requests.get(lookup_url).text
        soup = BeautifulSoup(html_content, "lxml")

        data = soup.find_all("div", attrs={'class':'inner'})

        search_results = [] #gets search results

        # if len(search_results) == 0:
        #     print("Cannot find song.")
        #     # self.song_url = None
        #     return None

        for n in range(len(data)):
            search_results.append({
                "name": data[n].find('h2', attrs={'class': 'entry-title'}).text,
                "link": data[n].find('a').get('href')
            })

            # print('\n', data[n].find('h2', attrs={'class': 'entry-title'}).text)
            # print(data[n].find('a').get('href'), '\n')

        # song_url = search_results[0]["link"] #returns first search result, faster
        # self.song_url = song_url
        # return song_url

        #finds best match from search results; edge case: Jap. Ver songs published later than Kor. Ver;
        #NEW Edge Cases: GFriend - Love Whisper, IZONE - Secret Story of the Swan, MAMAMOO - Starry Night

        name_offset = 999
        name_inquiry = set(f"{self.artist_name} {self.song_name}".split())

        for n in range(len(search_results)):
            try:
                temp = name_result
            except:
                pass
            name_result = set(search_results[n]["name"].split())
            difference = len(list(name_inquiry.difference(name_result)))

            # print(search_results[n]["name"], name_inquiry, name_result, '\n')
            if difference == name_offset:
                try:
                    if len(name_result) < len(temp):
                         song_url = search_results[n]["link"]
                         name_offset = difference
                except:
                    pass
            elif difference < name_offset:
                song_url = search_results[n]["link"]
                name_offset = difference

        print(song_url)
        self.song_url = song_url
        return song_url

        # with open('html.txt', 'w', encoding = "utf-8") as w:
        #     w.write(soup.prettify())
        # print(soup.prettify())

#  ========================================================================================== #

    def get_lyrics(self):
        song_url = self.get_url()
        if song_url == None:
            # self.lyrics = None
            return {
                "romanization": "Lyrics could not be found.",
                "native": "Lyrics could not be found.",
                "english": "Lyrics could not be found."
            }

        html_content = requests.get(self.song_url).text
        soup = BeautifulSoup(html_content, "lxml")

        data = soup.find("table", attrs={'border':'0'})
        if data == None:
            return {
                "romanization": "Lyrics could not be found.",
                "native": "Lyrics could not be found.",
                "english": "Lyrics could not be found."
            }

        parsed_data = []
        for td in data.findAll("td"):
            parsed_data.append(td)

        try:
            romanized_lyrics = parsed_data[0]
            native_lyrics = parsed_data[1]
            english_lyrics = parsed_data[2]
        except:
            if len(parsed_data) == 1:
                native_lyrics = [0]
                romanized_lyrics = "Lyrics could not be found."
                english_lyrics = "Lyrics could not be found."
            elif len(parsed_data) == 2:
                romanized_lyrics = [0]
                native_lyrics = [1]

        lyrics = {
            "romanization": str(romanized_lyrics),
            "native": str(native_lyrics),
            "english": str(english_lyrics)
        }

        # with open('lyrics.txt', 'w', encoding = "utf-8") as w:
        #     w.write(lyrics["native"])

        # print(parsed_data[0])
        # self.lyrics = lyrics
        #print(lyrics)
        return lyrics

        # print(soup.prettify())



####
# lyrics = ColorCodedLyrics(song_name = "Ding Ding Dong", artist_name = "LOONA")

# lyrics.get_url()
# lyrics.get_lyrics()
