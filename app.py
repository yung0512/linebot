import os
import sys
import json
import random
import requests
from bs4 import BeautifulSoup
import urllib
import lxml
import re
from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

from fsm import TocMachine
from utils import send_text_message

load_dotenv()


machine = TocMachine(
    states=["user", "state1", "state2"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state1",
            "conditions": "is_going_to_state1",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state2",
            "conditions": "is_going_to_state2",
        },
        {"trigger": "go_back", "source": ["state1", "state2"], "dest": "user"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)
def get_answer(message_text):

    url = "https://linebottest11.azurewebsites.net/qnamaker/knowledgebases/f0c4a997-31b0-4459-843c-233645a700fa/generateAnswer"
    response = requests.post(url,json.dumps({'question':message_text}),
                            headers={
                                    'Content-Type':'application/json',
                                    'Authorization':'EndpointKey 3fd131e6-6c93-4e74-89a3-d22bb47a5541'
                                     }

                              )
    # app.logger.info("test get_answer fcn"+response)
    data = response.json()
    
    try:
        if "error" in data:
          return data["error"]["message"]
        
        
        answer = data['answer']['0']['anwser']
        app.logger.info("test "+answer)
        return answer
    except Exception:
      
        return "Error occurs when finding anwser"


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
      #  response = machine.advance(event)
        question = {'tbm':'isch','q':event.message.text};
      #  if response == False:
      #      send_text_message(event.reply_token, "Not Entering any State")
      #  answer = get_answer(event.message.text)
        try:
            
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
     
            # for match in re.finditer(pattern, str(conn.read())):
            #     img_list.append(match.group()[14:-1])

             for d in image:
                  if d.find('img'):
                         result = d.find('img')['src']
                         print(result)
                         img_list.append(result)     
       
            
             random_img_url = img_list[random.randint(0, len(img_list)+1)]
             print('fetch img url finish')
             print(rand_img_url)
            
        
             line_bot_api.reply_message(
                 event.reply_token,
                 ImageSendMessage(
                     original_content_url=result,
                     preview_image_url=result
                 )
             )
        except:
             line_bot_api.reply_message(
                 event.reply_token,
                 TextSendMessage(text=event.message.text)
              
           )
        pass


             
      #  send_text_message(event.reply_token,answer)
    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
