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
material_class_dir = './material_class'
split_materials_dir = './split_materials'

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

# create the dirs
for d in [material_dir, material_class_dir, split_materials_dir]:
    if not os.path.exists(d):
        os.makedirs(d)


def fetch_captcha(size):
    '''
    获取原始用于标记训练的二维码，并写入materials_dir
    :param size:
    :return:
    '''
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
    所有待标注素材的类标号写入文本文件，自动读取并进行重命名。关于标注，需要自行解决。
    :return:
    '''
    class_str = ''
    for path, dirs, files in os.walk(material_class_dir):
        for f in files:
            with open(os.path.join(path, f)) as fp:
                class_str += fp.read().upper()

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
            parts = f.split('.')
            if parts[1] != 'gif':
                continue
            img = Image.open(os.path.join(path, f))
            w, h = img.size
            img = img.convert('L')
            img = img.point(lambda i: 0 if i < 120 else 255)

            # 寻找能够覆盖验证码有效图像的最小矩形
            left_top = (9999, 9999)
            right_bottom = (0, 0)
            for x in range(w):
                for y in range(h):
                    if img.getpixel((x, y)) == BLACK:
                        left_top = (min(x, left_top[0]), min(y, left_top[1]))
                    if img.getpixel((w - x - 1, h - y - 1)) == BLACK:
                        right_bottom = (max(w - x - 1, right_bottom[0]), max((h - y - 1), right_bottom[1]))

            # 进行适当缩放，使得最终截取大小与choose_frame一致
            w_diff = right_bottom[0] - left_top[0] + 1 - choose_frame[0]
            h_diff = right_bottom[1] - left_top[1] + 1 - choose_frame[1]
            crop_left_top = (left_top[0] + round(w_diff / 2), left_top[1] + round(h_diff / 2))

            img = img.crop((crop_left_top[0], crop_left_top[1],
                            choose_frame[0] + crop_left_top[0], choose_frame[1] + crop_left_top[1]))
            for i in range(4):
                cropped = img.crop(((i * choose_frame[0] / 4), 0, (i + 1) * choose_frame[0] / 4, choose_frame[1]))
                cropped.save(os.path.join(split_materials_dir, f.split('.')[0] + str(i) + '.jpg'))


if __name__ == '__main__':
    #fetch_captcha(5000)
    #mark_captcha()
    split_captcha()



