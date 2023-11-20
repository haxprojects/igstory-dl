import os
import requests
import json
from colorama import init, Fore
from datetime import datetime
import random

init(autoreset=True)

class InstagramStoryDownloader:
    def __init__(self, appId, userId, sessionId):
        self.instagramScraper = InstagramScraper(appId, userId, sessionId)

    def download_story(self, namaig):
        date_now = lambda: datetime.now().strftime('%H-%M-%S-%f')
        userID = self.instagramScraper.getUserID(namaig)

        if userID != 0:
            try:
                elements = []
                storyJson = self.instagramScraper.getStory(userID)

                if 'items' in storyJson.get('reels_media', [])[0]:
                    for item in storyJson['reels_media'][0]['items']:
                        # del item['url']
                        # del item['video_dash_manifest']
                        if 'video_versions' in item:
                            elements.append({
                                'type': 'video',
                                'data': item['video_versions'][0]
                            })
                        else:
                            elements.append({
                                'type': 'image',
                                'data': item['image_versions2']['candidates'][0]
                            })

                if elements:
                    try:
                        foldername = f'./temp/story/{namaig}'
                        os.makedirs(foldername, exist_ok=True)

                        print(f"[+] [{date_now()}] {Fore.YELLOW}Start Downloading story from {namaig}...")

                        i = 0
                        for x in elements:
                            current_time = datetime.now()
                            datenow = current_time.strftime('%Y-%m-%d').replace('/', '-')
                            time = current_time.strftime('%H-%M-%S-%f')[:-3]
                            rnd = random.randint(1111, 9999)
                            file_path = f'{foldername}/{datenow}-{time}-{rnd}'

                            if x['type'] == 'video':
                                # print(x['data'])
                                response = requests.get(x['data']['url'])
                                buffer = response.content
                                i += 1
                                print(f"[+] [{date_now()}] {Fore.GREEN}Downloading story {Fore.YELLOW}video{Fore.GREEN} from {Fore.CYAN}{namaig}{Fore.GREEN} {i} of {len(elements)}")
                                with open(f'{file_path}.mp4', 'wb') as file:
                                    file.write(buffer)
                            else:
                                response = requests.get(x['data']['url'])
                                buffer = response.content
                                i += 1
                                print(f"[+] [{date_now()}] {Fore.GREEN}Downloading story {Fore.YELLOW}image{Fore.GREEN} from {Fore.CYAN}{namaig}{Fore.GREEN} {i} of {len(elements)}")
                                with open(f'{file_path}.jpg', 'wb') as file:
                                    file.write(buffer)
                        print(f"[+] [{date_now()}] {Fore.MAGENTA}Download finished.")
                    except Exception as err:
                        print(f"[+] [{date_now()}] {Fore.RED}Error creating/checking folder: {err}")
                else:
                    print(f"[+] [{date_now()}] {Fore.RED}Username of {Fore.YELLOW}{namaig}{Fore.RED} is not found or does not have story, or the account is private.")
            except Exception as e:
                print(f"[+] [{date_now()}] {Fore.RED}Cookie is not valid, please check your config.json file.", e)
        else:
            print(f"[+] [{date_now()}] {Fore.RED}Error getting User-ID for {namaig}")

class InstagramScraper:
    def __init__(self, appId, userId, sessionId):
        self.headers = {
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded',
            'sec-fetch-site': 'same-site',
            'x-ig-app-id': appId,
            'cookie': f'ds_user_id={userId}; sessionid={sessionId};',
        }
        self.instagramApiBaseUrl = 'https://i.instagram.com/api/v1'

    def getUserID(self, username):
        try:
            response = requests.get(f'{self.instagramApiBaseUrl}/users/web_profile_info/?username={username}', headers=self.headers)
            json_data = response.json()
            # print(json_data)
            if json_data.get('status') == 'ok':
                return json_data['data']['user']['id']
            else:
                print(f'[+] Failed to get User-ID for {username}')
                return 0
        except Exception as error:
            print(f'[+] Error in loading user-id from {username}. Maybe the user doesn\'t exist!', error)
            return 0

    def getStory(self, userID):
        try:
            response = requests.get(f'https://www.instagram.com/api/v1/feed/reels_media/?reel_ids={userID}', headers=self.headers)
            return response.json()
        except Exception as error:
            print(f'[+] Error in fetching story for user with ID {userID}')
            raise error

if __name__ == "__main__":
    try:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)

        instagram_downloader = InstagramStoryDownloader(config.get("X-Ig-App-Id", ""), config.get("ds_user_id", ""), config.get("sessionid", ""))

        print(f"{Fore.CYAN}[>] Instagram story downloaders.")

        while True:
	        date_now = lambda: datetime.now().strftime('%H-%M-%S-%f')
	        namaig = input("[+] Instagram Username: ")
	        instagram_downloader.download_story(namaig)
	        print()
    except Exception as e:
        print(f"[+] [{date_now()}] {Fore.RED}Error: {e}")
