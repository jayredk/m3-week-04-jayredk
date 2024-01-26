from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from openai import OpenAI
from dotenv import load_dotenv

from commands import commands_info

load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('YOUR_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('YOUR_CHANNEL_SECRET'))

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_response(prompt, role="user"):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.lower()
    if msg.startswith('/echo '):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg[6:])
        )
    elif msg.startswith('/ask '):
        response = generate_response(msg[5:])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
    elif msg.startswith('/joke'):
        question = "你是一位說笑話的大師，擅長相聲、喜劇。用正體中文說一個笑話"
        response = generate_response(question)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
    elif msg.startswith('/djoke'):
        question = "告訴我一個 Dad joke，並用正體中文解釋給我聽"
        response = generate_response(question)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
    elif msg.startswith('/ts'):
        question = "接下來請以幹話的方式回覆我，我說的任何東西，請以幽默有趣的口吻回覆"
        response = generate_response(question)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
    elif msg.startswith('/normal'):
        question = "請恢復正常的回覆模式"
        response = generate_response(question)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
    elif msg.startswith('/ls'):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=commands_info)
        )
    else:
        response = '可以輸入 /ls 查看可用指令'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )

if __name__ == "__main__":
    app.run(debug=True)