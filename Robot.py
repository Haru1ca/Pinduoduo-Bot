import itchat, requests, re
from pandas import DataFrame
from urllib.request import quote
import traceback
import logging
import json, time
from itchat.content import *

###################
Api = "www.kemasu.site"
Nat = "https"
###################
Api_short = Nat + "://" + Api + "/Api/urlconvert.php"
Api_search = Nat + "://" + Api + "/Api/pddsearch.php"
Api_search2 = Nat + "://" + Api + "/Api/searchgood.php"
Api_search3 = Nat + "://" + Api + "/Api/getgood.php"
###################

def wx_send():
    recogood = requests.get(Api_search3)
    recogoodname = recogood.json()["goods_basic_detail_response"]["list"][0]["goods_name"]
    recogoodid = recogood.json()["goods_basic_detail_response"]["list"][0]["goods_sign"]
    recogooddesc = recogood.json()["goods_basic_detail_response"]["list"][0]["goods_desc"]
    recogoodprice = recogood.json()["goods_basic_detail_response"]["list"][0]["min_group_price"]
    recogoodcou = recogood.json()["goods_basic_detail_response"]["list"][0]["coupon_discount"]
    recoback = requests.get(Api_search2 + "?goodid=['" + recogoodid + "']")
    WANT_TO_SAY = '【今日推荐】'+'\n'+str(recogoodname)+'\n'+'【产品介绍】'+'\n'+str(recogooddesc)+'\n'+'【付费价】'+str(recogoodprice)+'\n【优惠券】'+str(recogoodcou)+'元\n【抢购链接】'+str(recoback.json()["goods_promotion_url_generate_response"]["goods_promotion_url_list"]["mobile_short_url"])
    itchat.auto_login(hotReload=True)
    friendList = itchat.get_friends(update=True)[1:]
    i=0
    for friend in friendList:
        i+=1
        itchat.send(WANT_TO_SAY % (friend['DisplayName'] or friend['NickName']))
        time.sleep(.3)

@itchat.msg_register(FRIENDS)
def add_friend(msg):
    msg.user.verify()
    msg.user.send('欢迎使用拼多多返现机器人，您可以发送商品链接至机器人，机器人会帮你抓取优惠券！')
    msg.user.send('使用教程：拼多多点击商品页右上角的分享按钮，选择“复制链接”，将纯链接发送至机器人即可查询优惠！')

@itchat.msg_register(itchat.content.TEXT)
def reply_self(msg):
    NickName = msg['User']['NickName']
    UserName = msg['User']['UserName']
    CreateTime = msg['CreateTime']
    print("发送者昵称：" + NickName + "发送者标识：" + UserName + "发送时间：" + str(CreateTime) + "发送的内容：" + msg['Text'])
    MsgUrl = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', msg['Text'])
    if MsgUrl[0] == nil or MsgUrl[0] == "":
        return str("请发送有效的链接！")
    back_short = requests.get(Api_short + "?url=" + MsgUrl[0])
    shangPin_url = back_short.json()["goods_zs_unit_generate_response"]["multi_group_short_url"]
    print("解析商品Api返回的url：" + str(shangPin_url))
    back_search = requests.get(API_search + "?keyword=" + str(shangPin_url))
    youhuijiage = back_search.json()["goods_search_response"]["goods_list"][0]["coupon_discount"]
    goodid = back_search.json()["goods_search_response"]["goods_list"][0]["goods_sign"]
    back_all = requests.get(Api_search2 + "?goodid=['" + goodid + "']")
    return str(back_search.json()["goods_search_response"]["goods_list"][0]["goods_name"])+'\n'+'【付费价】'+\
          str(back_search.json()["goods_search_response"]["goods_list"][0]["min_group_price"])\
          +'\n【优惠券】'+str(youhuijiage)+\
          '元\n【抢购链接】'+str(back_all.json()["goods_promotion_url_generate_response"]["goods_promotion_url_list"][0]["mobile_short_url"])

itchat.auto_login()
sched = BlockingScheduler()
sched.add_job(wx_send, 'cron', hour=24,minute=1,second=00)
sched.start()
itchat.run()