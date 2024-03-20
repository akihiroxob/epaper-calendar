#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pics')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'libs')
print(libdir);

if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in3f
import time
import datetime
from PIL import Image,ImageDraw,ImageFont,ImageEnhance
import traceback

logging.basicConfig(level=logging.DEBUG)

def getDayLeft():
    target_date = datetime.datetime(year=2024, month=10, day=23, hour=0)
    diff = target_date - datetime.datetime.now()
    return diff.days

def scale(image: Image, target_width=480, target_height=800) -> Image:
    """
    Given an Pillow image and the two dimensions scale it, 
    cropping centrally if required.
    """
    width, height = image.size
    if height/width < target_height/target_width:
        warn('too wide: cropping')
        new_height = target_height
        new_width = int(width * new_height / height)
    else:
        warn('too tall: cropping')
        new_width = target_width
        new_height = int(height * new_width / width)
    print(height, width, target_height, target_width, new_height, new_width)
    # Image.ANTIALIAS is depracated --> Image.Resampling.LANCZOS
    # but a fresh install of pillow via ``ARCHFLAGS='-arch arm6' python3 -m pip install pillow``
    # yielded 8.1.2 as of 26/02/23
    ANTIALIAS = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS
    img = image.resize((new_width, new_height), ANTIALIAS)
    # (left, top, right, bottom)
    half_width_delta = (new_width - target_width) // 2
    half_height_delta = (new_height - target_height) // 2
    img = img.crop((half_width_delta, half_height_delta,
                    half_width_delta + target_width, half_height_delta + target_height
                   ))
    return img

try:
    logging.info("epd7in3f Demo")

    epd = epd7in3f.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font40 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 40)
    font80 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 80)
    
#    # Drawing on the image
#    logging.info("1.Drawing on the image...")
#    Himage = Image.new('RGB', (epd.width, epd.height), epd.WHITE)  # 255: clear the frame
#    draw = ImageDraw.Draw(Himage)
#    draw.text((5, 0), 'hello world', font = font18, fill = epd.RED)
#    draw.text((5, 20), '7.3inch e-Paper (F)', font = font24, fill = epd.YELLOW)
#    draw.text((5, 45), u'微雪电子', font = font40, fill = epd.GREEN)
#    draw.text((5, 85), u'微雪电子', font = font40, fill = epd.BLUE)
#    draw.text((5, 125), u'微雪电子', font = font40, fill = epd.ORANGE)
#
#    draw.line((5, 170, 80, 245), fill = epd.BLUE)
#    draw.line((80, 170, 5, 245), fill = epd.ORANGE)
#    draw.rectangle((5, 170, 80, 245), outline = epd.BLACK)
#    draw.rectangle((90, 170, 165, 245), fill = epd.GREEN)
#    draw.arc((5, 250, 80, 325), 0, 360, fill = epd.RED)
#    draw.chord((90, 250, 165, 325), 0, 360, fill = epd.YELLOW)
#    epd.display(epd.getbuffer(Himage))
#    time.sleep(3)

    # read bmp file 
    logging.info("2.read bmp file")
    original_image = Image.open(os.path.join(picdir, '1001.001.jpeg'))

    enhanced_image: Image = ImageEnhance.Color(original_image).enhance(3)
    pal_image = Image.new("P", (1,1))
    pal_image.putpalette( (0,0,0,  255,255,255,  0,255,0,   0,0,255,  255,0,0,  255,255,0, 255,128,0) + (0,0,0)*249)
    endithered: Image = enhanced_image.convert("RGB").quantize(palette=pal_image)

    draw = ImageDraw.Draw(endithered)
    draw.rectangle((0, 520, 480, 800), fill = epd.WHITE)
    draw.text((160, 560), 'あと', font = font40, fill = epd.YELLOW)
    draw.text((160, 600), str(getDayLeft()), font = font80, fill = epd.WHITE)
    draw.text((300, 640), 'にち', font = font40, fill = epd.YELLOW)
    epd.display(epd.getbuffer(endithered))
    time.sleep(3)

    #logging.info("Clear...")
    #epd.Clear()
    
    logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in3f.epdconfig.module_exit(cleanup=True)
    exit()
