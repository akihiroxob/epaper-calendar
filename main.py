#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'libs')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in3f
import time
import datetime
import random
import json
import requests
from PIL import Image,ImageDraw,ImageFont,ImageEnhance

## get dir
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets/pics')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets/fonts')
icondir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets/icons')

def get_art_info():
    art_index_open = open(os.path.join(picdir, 'index.json'), 'r')
    return json.load(art_index_open)

def get_day_left():
    target_date = datetime.datetime(year=2024, month=10, day=23, hour=0)
    diff = target_date - datetime.datetime.now()
    return diff.days

def get_date(datetime):
    date = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
    return date[datetime.weekday()]

def resize_image(img, size):
    if (img.height > img.width):
        height = round(img.height * size / img.width)
        return img.resize((size, height))
    else:
        width = round(img.width * size / img.height)
        return img.resize((width, size))

def enhance_image(img):
    enhanced_image: Image = ImageEnhance.Color(img).enhance(3)
    pal_image = Image.new('P', (1,1))
    pal_image.putpalette( (0,0,0,  255,255,255,  0,255,0,   0,0,255,  255,0,0,  255,255,0, 255,128,0) + (0,0,0)*249)
    return enhanced_image.convert('RGB').quantize(palette=pal_image)

def get_today_forecast():
    url = 'https://api.weatherapi.com/v1/forecast.json'
    query = {
            'q': 'tokyo',
            'days': 1,
            'aqi': 'no',
            'alerts': 'no',
            'key': os.environ['WEATHER_APPID']
    }
    response = requests.get(url, params = query)
    if response.status_code == 200:
        data = response.json()
        return data['forecast']['forecastday'][0]['day']
    else:
        return False

try:
    logging.basicConfig(level=logging.DEBUG)
    logging.info('start drawing on epd7in3f')

    # setup
    ## setup fonts
    font8 = ImageFont.truetype(os.path.join(fontdir, 'Noto_Sans_JP/NotoSansJP-Bold.ttf'), 8)
    font10 = ImageFont.truetype(os.path.join(fontdir, 'Noto_Sans_JP/NotoSansJP-Bold.ttf'), 10)
    font16 = ImageFont.truetype(os.path.join(fontdir, 'Noto_Sans_JP/NotoSansJP-Regular.ttf'), 16)
    font20 = ImageFont.truetype(os.path.join(fontdir, 'Noto_Sans_JP/NotoSansJP-Bold.ttf'), 20)
    font28 = ImageFont.truetype(os.path.join(fontdir, 'Noto_Sans_JP/NotoSansJP-Bold.ttf'), 28)
    font32 = ImageFont.truetype(os.path.join(fontdir, 'Noto_Sans_JP/NotoSansJP-Bold.ttf'), 32)
    font40 = ImageFont.truetype(os.path.join(fontdir, 'Noto_Sans_JP/NotoSansJP-Bold.ttf'), 40)
    font68 = ImageFont.truetype(os.path.join(fontdir, 'Noto_Sans_JP/NotoSansJP-Bold.ttf'), 68)
    font80 = ImageFont.truetype(os.path.join(fontdir, 'Noto_Sans_JP/NotoSansJP-Bold.ttf'), 80)
    font100 = ImageFont.truetype(os.path.join(fontdir, 'Noto_Sans_JP/NotoSansJP-Bold.ttf'), 100)

    epd = epd7in3f.EPD()
    logging.info('init and Clear')
    epd.init()
    epd.Clear()

    # create base image
    logging.info('start to create image')
    background = Image.new('RGB', (epd.width, epd.height), epd.WHITE)  # 255: clear the frame

    # paste left side
    left_side = Image.new('RGB', (480, 480), epd.WHITE)  # 255: clear the frame
    i = random.randrange(58) + 1
    original_image = Image.open(os.path.join(picdir, f'picts.{i}.jpg'))
    resized_image = resize_image(original_image, 480)
    enhanced_image = enhance_image(resized_image)
    pos_left = round((480 - enhanced_image.width) / 2)
    pos_top = round((480 - enhanced_image.height) / 2)
    left_side.paste(enhanced_image, (pos_left, pos_top))

    ## write art info
    art_info = get_art_info()
    info_text = f'{art_info[str(i)]["title"]} | {art_info[str(i)]["artist"]}';
    write = ImageDraw.Draw(left_side)
    write.text((4, 466), info_text, font = font10, fill = epd.WHITE)
    background.paste(left_side, (0, 0))

    # create right side
    cover = Image.new('RGB', (320, 480), epd.WHITE)
    draw = ImageDraw.Draw(cover)

    today = datetime.datetime.now()
    draw.text((124, 32), str(today.year), font = font28, fill = epd.BLACK)
    draw.text((124, 64), f'令和{today.year - 2018}年', font = font20, fill = epd.BLACK)

    draw.text((92, 112), f'{today.month:02}月{today.day}日', font = font32, fill = epd.BLACK)
    draw.text((120, 148), get_date(today), font = font28, fill = epd.BLACK)

    ## wright weather info if get from weather api
    result = get_today_forecast()
    if result != False:
        weather_image = Image.open(os.path.join(icondir, f'weather/{result["condition"]["code"]}.jpg'))
        cover.paste(resize_image(weather_image, 32), (60, 192))
        draw.text((94,196), f'{result["maxtemp_c"]}/{result["mintemp_c"]}℃', font=font16, fill = epd.BLACK)
        humidity_image = Image.open(os.path.join(icondir, f'humidity.png'))
        cover.paste(resize_image(humidity_image, 20), (202, 198))
        draw.text((230,196), f'{result["avghumidity"]:02}%', font = font16, fill = epd.BLACK)

    draw.text((50, 296), '洗足学園小学校', font = font32, fill = epd.BLACK)
    draw.text((98, 338), '試験まで', font = font32, fill = epd.BLACK)
    draw.text((60, 368), str(get_day_left()), font = font80, fill = epd.BLACK)
    draw.text((212, 378), '日', font = font68, fill = epd.BLACK)
    background.paste(cover, (480, 0))

    # draw to epaper
    epd.display(epd.getbuffer(background))
    time.sleep(3)

    logging.info('Goto Sleep...')
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info('ctrl + c:')
    epd7in3f.epdconfig.module_exit(cleanup=True)
    exit()
