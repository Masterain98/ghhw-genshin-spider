import os
import json
import multitasking
import hashlib
import requests
import re

result_list = []


def need_cache(string_content: str) -> bool:
    if string_content.startswith("https://genshin.honeyhunterworld.com/"):
        if string_content.endswith(".png"):
            return True
    return False


def check_list(this_list: list):
    for this_item in this_list:
        if type(this_item) == str:
            if need_cache(this_item):
                result_list.append(this_item)
        elif type(this_item) == dict:
            check_dict(this_item)
        elif type(this_item) == list:
            check_list(this_item)


def check_dict(this_dict: dict):
    dict_values = this_dict.values()
    for value in dict_values:
        if type(value) == str:
            if need_cache(value):
                result_list.append(value)
        elif type(value) == dict:
            check_dict(value)
        elif type(value) == list:
            check_list(value)


@multitasking.task
def download_img(url, path, fileName):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'accept': "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-CN,zh;q=0.9,en;q=0.8",
        'referer': 'https://genshin.honeyhunterworld.com/?lang=EN'
    }
    fileName = hashlib.sha1(str.encode(url)).hexdigest() + ".png"
    if not os.path.exists(path):
        os.mkdir(path)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.content
        with open(path + fileName, mode='wb') as f:
            f.write(content)
        print("Downloaded: " + fileName)
    else:
        print("Status Code: " + str(response.status_code))


if __name__ == "__main__":
    file_list = [file for file in os.listdir('./') if file.endswith(".json")]
    for json_file in file_list:
        with open(json_file) as j:
            json_content = json.load(j)

        # Transverse the json content
        for item in json_content:
            if type(item) == str:
                if need_cache(item):
                    result_list.append(item)
            elif type(item) == dict:
                check_dict(item)
            elif type(item) == list:
                check_list(item)
    result_list = list(set(result_list))
    print("number of cache file: " + str(len(result_list)))
    print(result_list)
    for png in result_list:
        # print(re.search(r"(\w|\d|_)+(.png)", png).group())
        download_img(png, "./Cache/", re.search("(\w|\d)+(.png)", png).group())
    multitasking.wait_for_tasks()
    print("all done")
