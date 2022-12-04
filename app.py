from __future__ import unicode_literals
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage, ImageSendMessage
import json
import time
import configparser
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from detect import detect


app = Flask(__name__, static_url_path='/static')
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif','heif','heic'])

# 讀取linebot帳號授權
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))
my_line_id = config.get('line-bot', 'my_line_id')
end_point = config.get('line-bot', 'end_point')
line_login_id = config.get('line-bot', 'line_login_id')
line_login_secret = config.get('line-bot', 'line_login_secret')
my_phone = config.get('line-bot', 'my_phone')
HEADER = {
    'Content-type': 'application/json',
    'Authorization': F'Bearer {config.get("line-bot", "channel_access_token")}'
}
# ngrok 反向伺服器 重開ngrok要記得改
# 用 GCP 取代
ngrok_url = "https://7b88-2001-b011-6c00-59c3-5d3a-f3c6-a48-98df.jp.ngrok.io"


# 這是哪隻貓功能
@app.route("/", methods=['POST'])
def whatscat():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)

    except InvalidSignatureError:
        abort(400)

    return 'OK'

user_collection = {}
temp_userid = {}

global remain
remain = []
global cat
cat = ['躲貓貓Hide_And_Seek',
            '麻糬Mochi',
            '跩哥Malfoy',
            '瞌睡蟲Sleepy',
            '小孤獨Lonely',
            '阿虎Tiger',
            '豆花Douhua',
            '小花Flower',
            '美女Pretty_Girl',
            '膽小鬼Coward',
            '小妖豔Shower',
            '小淘氣Player',
            '小煤炭Soot_Spirits',
            '傑克Jack',
            '麒麟Kirin',
            '熊貓Panda',
            '站長Station_Master',
            '萱萱Xuan_Xuan',
            '跳跳虎Jumping_Tiger',
            '沃卡萊姆Vodka_Lime',
            '馬丁尼Martini',
            '莫希托Mojito']


# line_api 接收訊息
@handler.add(MessageEvent)
def handle_message(event):
    UserId = event.source.user_id
#   profile = line_bot_api.get_profile(UserId)
    print(UserId)


    if (event.message.type == "image"):
        SendImage = line_bot_api.get_message_content(event.message.id)
        path = './static/' + str(UserId)
        if not os.path.isdir(path):
            os.makedirs(path)
        local_save = path + '/' + event.message.id + '.png'

        with open(local_save, 'wb') as file:
            for chenk in SendImage.iter_content():
                file.write(chenk)
        print(local_save)

        # detect.py 基本輸入參數 記得另外寫json檔
        detect_args = """
        {
            "weights": [
                "22cat_best.pt"
            ],
            "source": "cat_test53.jpg",
            "img_size": 640,
            "conf_thres": 0.77,
            "iou_thres": 0.45,
            "device": "cpu",
            "view_img": true,
            "save_txt": false,
            "save_conf": false,
            "nosave": false,
            "classes": null,
            "agnostic_nms": false,
            "augment": false,
            "update": false,
            "project": "",
            "name": "",
            "exist_ok": false,
            "no_trace": true
        }
        """

        # 字串轉json格式
        json_args = json.loads(detect_args)
        opt = json_args
        # 將傳入照片來源改成flask預設圖片目錄
        opt["source"] = local_save
        # 呼叫detect功能
        result, photo_path = detect(opt, temp_userid)

        print('-----photo_path-----'+photo_path)
        clean_photo_path = photo_path[20:]
        print('-----clean_photo_path-----' + clean_photo_path)
        # user_collection[temp_userid] = photo_path
        # print('user_collection' + ('-' * 30))
        # print(user_collection)


        print('------按以下連結---------')
        print(ngrok_url + "/static/result_photo/" + clean_photo_path)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))

        feedback = []
        new_result = result[:-5]
        feedback.append(new_result)
        # print(feedback)

        for i in feedback:
            if i in remain:
                pass
            elif i in cat:
                remain.append(i)
                print(remain)
                cat.remove(i)
                print(cat)
            print("您目前已收集" + str(remain))
            print("您目前還剩下" + str(cat))
            reply_remain = "您目前已收集" + str(remain)
            reply_cat = "您目前還剩下" + str(cat)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_remain))
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_cat))

        time.sleep(1),
        line_bot_api.reply_message(event.reply_token, ImageSendMessage(
            original_content_url=ngrok_url + "/static/result_photo/" + clean_photo_path,
            preview_image_url=ngrok_url + "/static/result_photo/" + clean_photo_path))







# 執行此程式
if __name__ == "__main__":
    app.debug = True
    app.run()

