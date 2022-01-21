from PIL import Image, ImageDraw
from PIL import ImageFont
import datetime
from database_study import DBupdater
from io import BytesIO


class week_table:
    def __init__(self, name):
        self.im = None
        self.filename = "./week_table.png"
        self.font_name = "./.fonts/my_font.ttf"
        self.db = DBupdater()
        self.name = name

    # week_table.png 파일이 있는지 체크, 없으면 get_week_table 파일 만듬
    def check_file_exists(self):
        try:
            self.im = Image.open(self.filename)
        except IOError:
            self.make_week_table()
            self.im = open(self.filename, "rb")

    def make_week_table(self) -> None:

        font = ImageFont.truetype(self.font_name, 75)

        date_im = []
        menu_im = []
        date_name = ["월", "화", "수", "목", "금", "토", "일"]
        menu_name = ["공부 시간", "달성 여부"]
        date_colors = [(77, 137, 99), (105, 165, 131), (225, 179, 120), (224, 204, 151), (236, 121, 154), (159, 2, 81),
                       (127, 23, 255)]
        menu_colors = [(206, 235, 251), (163, 214, 245), (102, 167, 197)]

        self.im = Image.new(mode="RGB", size=(960, 270), color=(255, 255, 255))
        line = Image.new("RGB", (120, 90), (230, 230, 230))
        d = ImageDraw.Draw(self.im)

        # 날짜 이미지 추가
        for date in range(0, 7):
            date_im.append(Image.new("RGB", (120, 90), date_colors[date]))
            self.im.paste(date_im[date], ((date + 1) * 120, 0))
            d.text(((date + 1) * 120 + 40, -5), date_name[date], font=font, fill=(0, 0, 0))
        date_draw = ImageDraw.Draw(self.im)

        font = ImageFont.truetype(self.font_name, 45)
        # 메뉴 이미지 추가
        for menu in range(0, 2):
            menu_im.append(Image.new("RGB", (120, 90), menu_colors[menu]))
            self.im.paste(menu_im[menu], (0, menu * 90 + 90))
            d.text((10, menu * 90 + 100), menu_name[menu], font=font, fill=(0, 0, 0))

        # 격자 무늬 추가
        for row in range(1, 4):
            for col in range(1, 8):
                if (row + col) % 2 == 1:
                    self.im.paste(line, (120 * col, 90 * row))
        self.im.save(self.filename)

    def add_data(self):
        day_to_int = {"Monday" : 0, "Tuesday" : 1, "Wednesday" : 2, "Thursday" : 3, "Friday" : 4, "Saturday" : 5, "Sunday" : 6}
        seven_days = {}
        # wee_table.png 불러오기
        self.check_file_exists()
        # 오늘의 요일의 int값
        today_day_int = day_to_int[datetime.datetime.now().date().strftime("%A")]
        # 이번주의 월요일 날짜
        date_of_monday = datetime.datetime.now().date() - datetime.timedelta(days = today_day_int)
        date_of_sunday = date_of_monday + datetime.timedelta(days = 6)

        for day in range(7):
            seven_days[date_of_monday + datetime.timedelta(days = day)] = None

        db_seven_days = self.db.get_seven_days(self.name, date_of_monday, date_of_sunday)
        print(db_seven_days)



