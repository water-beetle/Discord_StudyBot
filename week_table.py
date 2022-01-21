from PIL import Image, ImageDraw
from PIL import ImageFont
from io import BytesIO


def get_week_table():
    date_im = []
    menu_im = []
    date_colors = [(77, 137, 99), (105, 165, 131), (225, 179, 120), (224, 204, 151), (236, 121, 154), (159, 2, 81),
                   (127, 23, 255)]
    menu_colors = [(206, 235, 251), (163, 214, 245), (102, 167, 197)]

    im = Image.new(mode="RGB", size=(800, 200), color=(255, 255, 255))
    line = Image.new("RGB", (100, 50), (230, 230, 230))
    blank = Image.new("RGB", (2, 200), (0, 0, 0))

    # 날짜 이미지 추가
    for date in range(0, 7):
        date_im.append(Image.new("RGB", (100, 50), date_colors[date]))
        im.paste(date_im[date], ((date + 1) * 100, 0))
    date_draw = ImageDraw.Draw(im)

    # 메뉴 이미지 추가
    for menu in range(0, 3):
        menu_im.append(Image.new("RGB", (100, 50), menu_colors[menu]))
        im.paste(menu_im[menu], (0, menu * 50 + 50))
    date_draw.text((0, 50), "a", fill=(0, 0, 0))

    # 격자 무늬 추가
    for row in range(1, 4):
        for col in range(1, 8):
            if (row + col) % 2 == 1:
                im.paste(line, (100 * col, 50 * row))
    im.show()
    return im
