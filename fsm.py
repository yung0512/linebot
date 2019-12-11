from transitions.extensions import GraphMachine
from utils import send_text_message, send_image_url
import requests
from bs4 import BeautifulSoup
import urllib
import lxml
import re
#import urllib2
#import pprint

wheather = {'台北市':'1','高雄市':'2','基隆':'3','台北':'4','桃園':'5','新竹':'6'
             ,'苗栗':'7','台中':'8','彰化':'9','南投':'10','雲林':'11','嘉義':'12'
            ,'台南':'13','高雄':'14','屏東':'15','恆春':'16','宜蘭':'17','花蓮':'18'
            ,'台東':'19','澎湖':'20','金門':'21','馬祖':'22'}


def getweather(id):

    result=''

    url='http://twweatherapi.appspot.com/forecast?location='+id+'&output=json'


    #first = urllib.request.Request(url, headers = headers)
    req=urllib.request.urlopen(url)
    test = req.full_url
    print(test)
    chiadict=eval(req.read())

    result=result+chiadict['result']['locationName']+' 天氣\n'

    result+="="*10

    result+="\n"

    for d in chiadict['result']['items']:

        result+=''+d['title']+'\n'

        result+='時間 '+d['time']+'\n'

        result+='天氣狀況 '+d['description']+'\n'

        result+='溫度 '+d['temperature']+' 度'+'\n'

        result+='降雨機率 '+d['rain']+' %\n'

        result+='-'*10

        result+="\n"

    return result



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

         send_image_url(event.reply_token, random_img_url)

    except:
            send_text_message(event.reply_token,event.message.text)
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
        return text.lower() == "weather"

    def is_going_to_state4(self, event):
        text = event.message.text
        return text.lower() == event.message.text

    def on_enter_state3(self, event):
        print("enter location")
        send_text_message(event.reply_token,"enter location")
        #self.go_back()

    def on_enter_state4(self, event):
        print("test state4")
        id = wheather[event.message.text]
        try:
             answer = getweather(id)
             send_text_message(event.reply_token,answer)
        except:
             send_text_message(event.reply_token,"sorry have some errors!!")
             self.go_back()
             pass

    def on_enter_state1(self, event):
        print("finding image state1")
        reply_token = event.reply_token
        send_text_message(reply_token, "please enter what image want to find")
        #self.go_back()

    def on_exit_state3(self,event):
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


    def on_exit_state4(self):
          print("Leaving state4")
