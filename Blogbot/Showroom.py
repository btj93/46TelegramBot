import requests
import json
from pyquery import PyQuery as pq
from Blogbot.Class.Blog import headers
import websockets
import time
import asyncio
from Blogbot.IO import readData, writeData, showroomfilename, blogfilename
import multiprocessing
import Blogbot.telegram as telegram
import datetime
import traceback



apiheaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/56.0.2924.76 Safari/537.36',
              "Upgrade-Insecure-Requests": "1",
              "DNT": "1",
              "Accept": "application/json",
              "Accept-Language": "en-US,en;q=0.5",
              "Accept-Encoding": "gzip, deflate"}


def nextLiveApiHelper(showroomdata):
    try:
        if showroomdata['ID'] != '':
            endpoint = f'https://www.showroom-live.com/api/room/next_live?room_id={showroomdata["ID"]}'
            with requests.get(endpoint, headers=apiheaders) as response:
                if response.status_code == 200:
                    return json.loads(response.text)
                else:
                    return None
        else:
            return {
                "epoch": None,
                "text": "TBD"
            }
    except requests.exceptions.ConnectionError as e:
        telegram.send_text(telegram.logchat_id, traceback.format_exc())
        return None


def getm3u8link(showroomdata):
    if showroomdata['ID'] != '':
        endpoint = f'https://www.showroom-live.com/api/live/streaming_url?room_id={showroomdata["ID"]}'
        with requests.get(endpoint, headers=apiheaders) as response:
            if response.status_code == 200:
                j = json.loads(response.text)['streaming_url_list']
                return max(j, key=lambda elem: elem['quality'])['url']


def getWebsocketStuffs(url):
    with requests.get(url, headers=headers) as response:
        if response.status_code == 200:
            data = json.loads(pq(response.text)('script[id=js-live-data]').attr('data-json'))
            result = {k: v for k, v in data.items() if k in ['broadcast_key', 'broadcast_host', 'broadcast_port']}
            return result


async def wss(group, member, data):
    while True:
        try:
            d = getWebsocketStuffs(data['URL'])
            if d is not None:
                if ':' not in d["broadcast_key"]:
                    async with websockets.connect(f'wss://{d["broadcast_host"]}/', max_queue=100,
                                                  ping_interval=60) as websocket:
                        await websocket.send(f'SUB\t{d["broadcast_key"]}')
                        print(member, data, d)
                        telegram.send_text(telegram.logchat_id, f"Websocket Connected to {member}")
                        print('start to monitor')
                        while True:
                            a = await websocket.recv()
                            print(a)
                            v = json.loads(a.split('\t')[-1])
                            print(v)
                            if v['t'] == 101:
                                time.sleep(300)
                                print('finish')
                                break
                            elif v['t'] == 104:
                                print('start')
                                key = member
                                # if member in ['林瑠奈', '黒見明香', '松尾美佑', '弓木奈於', '佐藤璃果']:
                                #     key = '新4期生リレー'
                                sendList = readData(blogfilename)[group][key]
                                m3u8 = getm3u8link(data)
                                for chatid in sendList:
                                    telegram.send_text(chatid, f'#{member} is now Live!\n{data["URL"]}\n\n{m3u8}')
                                break
                        print('checking done')
                else:
                    print('now live')
                    telegram.send_text(telegram.logchat_id, f'{member} now live')
                    await asyncio.sleep(60)
            else:
                telegram.send_text(telegram.logchat_id, "Failed. Retrying in 10 minutes")
                await asyncio.sleep(600)
        except Exception as e:
            print(traceback.format_exc())
            telegram.send_text(telegram.logchat_id, e)
            await asyncio.sleep(60)


async def NextLiveHandler():
    while True:
        # -----------------------------------------------------------------------------
        # telegram.send_text(telegram.logchat_id, 'Start seaching nextLive')
        # print(datetime.datetime.now())
        # prevData = readData(showroomfilename)
        # for group, members in prevData.items():
        #     summary = f'{group}:\n'
        #     with multiprocessing.Pool() as pool:
        #         newData = pool.map(nextLiveApiHelper, [data for member, data in members.items()])
        #     for member, nd in zip(members.keys(), newData):
        #         summary = summary + f'{member}: {nd}\n'
        #         data = members[member]
        #         print(member, data['nextLive'], nd)
        #         if nd is not None:
        #             if nd != data['nextLive'] and nd['text'] != 'TBD':
        #                 key = member
        #                 # if member in ['林瑠奈', '黒見明香', '松尾美佑', '弓木奈於', '佐藤璃果']:
        #                 #     key = '新4期生リレー'
        #                 sendList = readData(blogfilename)[group][key]
        #                 for chatid in sendList:
        #                     telegram.send_text(chatid, f'#{member}\nNext Live: {nd["text"]} JST\n\n{data["URL"]}')
        #                 prevData[group][member]['nextLive'] = nd
        #     # telegram.send_text(telegram.logchat_id, summary)
        # writeData(prevData, showroomfilename)
        # telegram.send_text(telegram.logchat_id, 'Finish seaching nextLive')
        # await asyncio.sleep(480)
        # ------------------------------------------------------------------------------
        try:
            print(datetime.datetime.now())
            prevData = readData(showroomfilename)
            for group, members in prevData.items():
                telegram.send_text(telegram.logchat_id, f'Start seaching {group} nextLive')
                with multiprocessing.Pool() as pool:
                    newData = pool.map(nextLiveApiHelper, [data for member, data in members.items()])
                for member, nd in zip(members.keys(), newData):
                    data = members[member]
                    print(member, data['nextLive'], nd)
                    if nd is not None and nd != data['nextLive'] and nd['text'] != 'TBD':
                        key = member
                        # if member in ['林瑠奈', '黒見明香', '松尾美佑', '弓木奈於', '佐藤璃果']:
                        #     key = '新4期生リレー'
                        sendList = readData(blogfilename)[group][key]
                        for chatid in sendList:
                            telegram.send_text(chatid, f'#{member}\nNext Live: {nd["text"]} JST\n\n{data["URL"]}')
                    prevData[group][member]['nextLive'] = nd
                # telegram.send_text(telegram.logchat_id, summary)
                writeData(prevData, showroomfilename)
                telegram.send_text(telegram.logchat_id, f'Finish seaching {group} nextLive')
                await asyncio.sleep(180)
        except Exception as e:
            print(traceback.format_exc())
            telegram.send_text(telegram.logchat_id, e)
            await asyncio.sleep(60)



async def invoke_both():
    await asyncio.gather(
        *[wss(group, member, s) for group, members in readData(showroomfilename).items() for member, s in
          members.items()
          if s['URL'] != ''], NextLiveHandler())



if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(invoke_both())

