from transitions.extensions import GraphMachine

from utils import send_text_message

import requests
from bs4 import BeautifulSoup
import urllib
import lxml
import re

check = 0

def findimage(event):
    try:
         question = {'tbm':'isch','q':event.message.text};
         url = f"https://www.google.com/search?{urllib.parse.urlencode(question)}/"
         headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}

         req = urllib.request.Request(url, headers = headers)
         conn = urllib.request.urlopen(req)
         test = req.full_url
         print(test)
         print('fetch page finish')
         rl = requests.get(test)
         soup = BeautifulSoup(rl.text,'lxml')
         image = soup.find_all('div')
         pattern = 'img data-src="\S*"'
         img_list = []
         for d in image:
              if d.find('img'):
                     result = d.find('img')['src']
                     print(result)
                     img_list.append(result)


         random_img_url = img_list[0]
         print('fetch img url finish')
         print(random_img_url)


         #line_bot_api.reply_message(
        #     event.reply_token,
        #     ImageSendMessage(
        #         original_content_url=random_img_url,
        #         preview_image_url=random_img_url
        #     )
        # )
         send_image_url(event.reply_token, random_img_url)

    except:
             line_bot_api.reply_message(
             event.reply_token,
             TextSendMessage(text=event.message.text)

         )
             pass

             return


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_state1(self, event):
        text = event.message.text
        return text.lower() == "image"

    def is_going_to_state2(self, event):
        text = event.message.text
        return text.lower() == event.message.text
    def is_going_to_state3(self, event):
        text = event.message.text
        return text.lower() == "test"

    def on_enter_state3(self, event):
        print("test state3")
        self.go_back()

    def on_enter_state1(self, event):
        print("finding image state1")
        reply_token = event.reply_token
        send_text_message(reply_token, "please enter what image want to find")
        #self.go_back()

    def on_exit_state3(self):
            print("Leaving state3")


    def on_exit_state1(self,event):
        print("Leaving state1")

    def on_enter_state2(self, event):
        print("I'm entering state2")

        reply_token = event.reply_token
        #send_text_message(reply_token, "Trigger state2")
        findimage(event)
        print("find!!!")
        self.go_back()

    def on_exit_state2(self):
        print("Leaving state2")
