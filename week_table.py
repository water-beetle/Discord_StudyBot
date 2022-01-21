from PIL import Image, ImageDraw
from PIL import ImageFont
from io import BytesIO


def get_week_table():
    date_im = []
    menu_im = []
    date_colors = [(77, 137, 99), (105, 165, 131), (225, 179, 120), (224, 204, 151), (236, 121, 154), (159, 2, 81),
                   (127, 23, 255)]
    menu_colors = [(206, 235, 251), (163, 214, 245), (102, 167, 197)]

    im = Image.new(mode="RGB", size=(1600, 400), color=(255, 255, 255))
    line = Image.new("RGB", (200, 100), (230, 230, 230))

    # 날짜 이미지 추가
    for date in range(0, 7):
        date_im.append(Image.new("RGB", (200, 100), date_colors[date]))
        im.paste(date_im[date], ((date + 1) * 200, 0))
    date_draw = ImageDraw.Draw(im)

    # 메뉴 이미지 추가
    for menu in range(0, 3):
        menu_im.append(Image.new("RGB", (200, 100), menu_colors[menu]))
        im.paste(menu_im[menu], (0, menu * 100 + 100))
    date_draw.text((0, 50), "a", fill=(0, 0, 0))

    # 격자 무늬 추가
    for row in range(1, 4):
        for col in range(1, 8):
            if (row + col) % 2 == 1:
                im.paste(line, (200 * col, 100 * row))
    im.show()
    return im
