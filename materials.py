#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: materials.py
@time: 07/06/2018 17:39
"""
import requests
import json
import base64
import os
from PIL import Image

material_dir = './materials'

headers = {'Connection': 'keep-alive',
           'Cache-Control': 'max-age=0',
           'Accept': '*/*',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/66.0.3359.181 Safari/537.36',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
           'Content-Type': 'application/json'}

BLACK = 0
WHITE = 255


def fetch_captcha(size):
    for i in range(size):
        try:
            resp = requests.get('https://sso.toutiao.com/refresh_captcha/',
                                params={'method': 'account_login'},
                                headers=headers)
            rtn = json.loads(resp.content)
            with open('%s/%d.gif' % (material_dir, i), 'ab') as f:
                f.write(base64.b64decode(rtn['captcha']))
        except Exception as e:
            print(e)


def mark_captcha():
    '''
    使用语音输入法，得到所有待标注素材的类标号，自动进行重命名
    :return:
    '''
    # for path, dirs, files in os.walk()
    class_str = 'arm5nrf6hdns'.upper()
    idx = 0
    length = 4
    for path, dirs, files in os.walk(material_dir):
        for f in files:
            cls = class_str[idx:idx+length]
            idx += length
            parts = f.split('.')
            if len(parts) == 2:
                os.rename(os.path.join(path, f), os.path.join(path, '%s.%s.%s' % (parts[0], cls, parts[1])))


def split_captcha():
    # 截取大小 width=64 height=18
    choose_frame = (64, 18)
    for path, dirs, files in os.walk(material_dir):
        for f in files:
            img = Image.open(os.path.join(path, f))
            w, h = img.size
            img = img.convert('L')
            img = img.point(lambda i: 0 if i < 120 else 255)
            img.show()

            split_points = [20, 30, 40]
            left_top = (9999, 9999)
            right_bottom = (0, 0)
            for x in range(w):
                for y in range(h):
                    if img.getpixel((x, y)) == BLACK:
                        left_top = (min(x, left_top[0]), min(y, left_top[1]))
                    if img.getpixel((w - x - 1, h - y - 1)) == BLACK:
                        right_bottom = (max(w - x - 1, right_bottom[0]), max((h - y - 1), right_bottom[1]))

            w_diff = right_bottom[0] - left_top[0] + 1 - choose_frame[0]
            h_diff = right_bottom[1] - left_top[1] + 1 - choose_frame[1]
            crop_left_top = (left_top[0] + round(w_diff / 2), left_top[1] + round(h_diff / 2))

            img = img.crop((crop_left_top[0], crop_left_top[1],
                      choose_frame[0] + crop_left_top[0], choose_frame[1] + crop_left_top[1]))
            for i in range(4):
                croped = img.crop(((i * choose_frame[0] / 4), 0, (i + 1) * choose_frame[0] / 4, choose_frame[1]))
                croped.show()
            img.show()


            for point in split_points:
                pass


if __name__ == '__main__':
    fetch_captcha(5000)
    #mark_captcha()
    #split_captcha()



