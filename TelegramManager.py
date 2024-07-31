from Constant import Config
import httpx
import threading
import os
import json

base_dir = os.path.dirname(__file__)
data_file = os.path.join(base_dir, 'contents')


class TelegramController():
    def __init__(self) -> None:
        super().__init__()
        self.url = f'{Config.TELEGRAM_URL}{self.get_default_token}'.strip()
        self.timeout = int(Config.TELEGRAM_REQUEST_TIMEOUT)


    def send_message(self, message: str, group: str|int) -> dict:
        payload = {
            'chat_id': group,
            'text': message
        }
        res = httpx.post(f'{self.url}/sendMessage', json=payload, timeout=self.timeout).json()
        print(res, payload)
    

    def broadcast_message(self, message: str, targets: list) -> None:
        threads = []
        for group in targets:
            work = threading.Thread(target=self.send_message, args=(message, group, ))
            threads.append(work)
            work.start()

        for thread in threads:
            thread.join()


    def sync_groups_channels(self) -> tuple:
        param = {}
        last_id = self.get_last_update_id()
        if last_id:
            param['offset'] = int(last_id)

        fpath = f'{data_file}/data.json'
        res = httpx.get(f'{self.url}/getupdates', timeout=self.timeout, params=param).json()
        data = {}
        channel_count = 0
        group_count = 0
        left_members = []
        if 'result' in res:
            results = res['result']
            for member in results:
                if 'my_chat_member' in member and member['my_chat_member']['chat']['type'] in [Config.CHAT_TYPE_GROUP, Config.CHAT_TYPE_CHANNEL, Config.CHAT_TYPE_SUPER_GROUP]:
                    data[member['my_chat_member']['chat']['id']] = member['my_chat_member']['chat']
                    if member['my_chat_member']['chat']['type'] == Config.CHAT_TYPE_CHANNEL:
                        channel_count += 1

                    if member['my_chat_member']['chat']['type'] in [Config.CHAT_TYPE_GROUP, Config.CHAT_TYPE_SUPER_GROUP]:
                        group_count += 1

                if 'message' in member and 'new_chat_member' in member['message'] and \
                    member['message']['new_chat_member']['is_bot'] and \
                    member['message']['new_chat_member']['username'] == self.get_default_username and \
                    member['message']['chat']['type'] in [Config.CHAT_TYPE_GROUP, Config.CHAT_TYPE_CHANNEL, Config.CHAT_TYPE_SUPER_GROUP]:
                    data[member['message']['chat']['id']] = member['message']['chat']
                    if member['message']['chat']['type'] == Config.CHAT_TYPE_CHANNEL:
                        channel_count += 1

                    if member['message']['chat']['type'] in [Config.CHAT_TYPE_GROUP, Config.CHAT_TYPE_SUPER_GROUP]:
                        group_count += 1

                if 'message' in member and 'new_chat_title' in member['message']:
                    data[member['message']['chat']['id']] = member['message']['chat']

                if 'message' in member and 'left_chat_member' in member['message'] and \
                    member['message']['left_chat_member']['is_bot'] and \
                    member['message']['left_chat_member']['username'] == self.get_default_username:
                    left_members.append(member['message']['chat']['id'])

            # Update id
            self.update_id(results)
            print(results)
        if os.path.exists(fpath):
            with open(fpath) as f:
                existing = json.load(f)
                for member in left_members:
                    if str(member) in existing:
                        del existing[str(member)]

            if existing:
                for k, v in existing.items():
                    data[int(k)] = v

        with open(fpath, 'w+') as f:
            f.write(json.dumps(data, indent=4))
            
        return (channel_count, group_count)
    

    def get_groups_channels(self, type: list = []) -> dict:
        file = f'{data_file}/data.json'
        if not os.path.exists(file): return []
        with open(file) as f:
            items = json.load(f)
            data = []
            for item in items:
                if items[item]['type'] in type:
                    data.append(items[item])

            return data
        

    def send_pictures(self, group: str, pictures: list, caption: str = None):
        media = {}
        items = []
        for i, pic in enumerate(pictures):
            f = open(pic, 'rb')
            media[f'pic_{i}'] = f
            items.append(
                {
                    'media': f'attach://pic_{i}',
                    'type': 'photo'
                }
            )

        items[0]['caption'] = caption if caption else ''
        payload = {
            'chat_id': group,
            'media': json.dumps(items)
        }
        res = httpx.post(f'{self.url}/sendMediaGroup', data=payload, files=media, timeout=self.timeout).json()
        try: 
            for m in media: m.close()
        except: pass
        return res


    def send_thread_pictures(self, targets: list, pictures: list, caption: str = None):
        threads = []
        for group in targets:
            work = threading.Thread(target=self.send_pictures, args=(group, pictures, caption, ))
            threads.append(work)
            work.start()

        for thread in threads:
            thread.join()

    
    def send_videos(self, group: str, videos: list, caption: str = None):
        media = {}
        items = []
        for i, pic in enumerate(videos):
            f = open(pic, 'rb')
            media[f'pic_{i}'] = f
            items.append(
                {
                    'media': f'attach://pic_{i}',
                    'type': 'video',
                    'width': 1280,
                    'height': 680
                }
            )

        items[0]['caption'] = caption if caption else ''
        payload = {
            'chat_id': group,
            'media': json.dumps(items)
        }
        res = httpx.post(f'{self.url}/sendMediaGroup', data=payload, files=media, timeout=self.timeout).json()
        try: 
            for m in media: m.close()
        except: pass
        return res


    def send_thread_videos(self, targets: list, videos: list, caption: str = None):
        threads = []
        for group in targets:
            work = threading.Thread(target=self.send_videos, args=(group, videos, caption, ))
            threads.append(work)
            work.start()

        for thread in threads:
            thread.join()


    def send_docs(self, group: str, docs: list, caption: str = None):
        media = {}
        items = []
        for i, pic in enumerate(docs):
            f = open(pic, 'rb')
            media[f'pic_{i}'] = f
            items.append(
                {
                    'media': f'attach://pic_{i}',
                    'type': 'document'
                }
            )

        items[0]['caption'] = caption if caption else ''
        payload = {
            'chat_id': group,
            'media': json.dumps(items)
        }
        res = httpx.post(f'{self.url}/sendMediaGroup', data=payload, files=media, timeout=self.timeout).json()
        try: 
            for m in media: m.close()
        except: pass
        return res


    def send_thread_docs(self, targets: list, docs: list, caption: str = None):
        threads = []
        for group in targets:
            work = threading.Thread(target=self.send_docs, args=(group, docs, caption, ))
            threads.append(work)
            work.start()

        for thread in threads:
            thread.join()


    def configure_bot(self, bot_name: str, bot_username: str, bot_token: str) -> bool:
        try:
            with open(f'{data_file}/bot.json', 'w+') as f:
                data = {}
                data[bot_username] = {
                    'name': bot_name,
                    'token': bot_token,
                    'username': bot_username
                }
                f.write(json.dumps(data, indent=4))
                return True
        except (Exception) as e: return e


    def show_bots(self) -> list:
        fname = f'{data_file}/bot.json'
        if not os.path.exists(fname): return []
        
        with open(fname) as f:
            data = []
            bots = json.load(f)
            for bot, v in bots.items():
                data.append(v)

            return data
        

    @property
    def get_default_token(self) -> dict:
        fname = f'{data_file}/bot.json'
        if not os.path.exists(fname): return None
        
        with open(fname) as f:
            bots = json.load(f)
            for _, v in bots.items():
                return v['token']
            

    @property
    def get_default_username(self) -> dict:
        fname = f'{data_file}/bot.json'
        if not os.path.exists(fname): return None
        
        with open(fname) as f:
            bots = json.load(f)
            for _, v in bots.items():
                return v['username']
            

    def get_last_update_id(self) -> int | None:
        fname = f'{data_file}/update_id.txt'
        if not os.path.exists(fname): return None
        with open(fname) as f: return f.readline()


    def update_id(self, results):
        fname = f'{data_file}/update_id.txt'
        if results:
            last_id = results[-1:][0]['update_id']
            with open(fname, 'w+') as f:
                f.write(str(last_id))