import pymysql
from datetime import datetime
# from dotenv import load_dotenv
import os

# load_dotenv()
PASSWORD = os.environ.get('PASSWORD')
USER = os.environ.get('USER')
HOST = os.environ.get('HOST')
DBTITLE = os.environ.get('DBTITLE')

class DBupdater:
    def __init__(self):
        """생성자 : MariaDB 연결 및 딕셔너리 생성"""
        self.conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DBTITLE,
                                    charset='utf8', port=3306)

        with self.conn.cursor() as curs:
            sql = """
            CREATE TABLE IF NOT EXISTS attend_date (
                `user_name` VARCHAR(20) NOT NULL COLLATE 'utf8mb3_general_ci',
                `today_study_time` TIME NULL DEFAULT NULL,
                `today_date` DATETIME NOT NULL,
                `is_achieve` TINYINT(2) NULL DEFAULT NULL,
                PRIMARY KEY (`user_name`, `today_date`) USING BTREE
            )
            COLLATE='utf8mb3_general_ci'
            ENGINE=InnoDB;
            """
            curs.execute(sql)
            sql = """
            CREATE TABLE IF NOT EXISTS attend_info (
                `user_name` VARCHAR(20) NOT NULL COLLATE 'utf8mb3_general_ci',
                `total_study_time` TIME NULL DEFAULT NULL,
                `target_time` TIME NULL DEFAULT NULL,
                PRIMARY KEY (`user_name`) USING BTREE
            )
            COLLATE='utf8mb3_general_ci'
            ENGINE=InnoDB;
            """
            curs.execute(sql)
        self.conn.commit()

    def __del__(self):
        """소멸자 : MariaDB 연결 해제"""
        self.conn.close()

    # !등록
    def update(self, name) -> None:
        with self.conn.cursor() as curs:
            sql = f"""INSERT INTO attend_info(user_name, total_study_time, target_time) VALUES('{name}', 
            '00:00:00',  '00:00:00') """
            curs.execute(sql)
        self.conn.commit()

    # 등록된 사용자인지 검사
    def is_admit(self, name)->bool:
        with self.conn.cursor() as curs:
            sql = f"""
            SELECT user_name FROM attend_info
            WHERE user_name="{name}"
            """
            curs.execute(sql)
            result = curs.fetchone()
        return result is None

    # attend_info에 [이름, 날짜]가 저장되어있는지 확인
    def is_admit_today(self, name, date)->bool:
        with self.conn.cursor() as curs:
            sql = f"""
            SELECT * FROM attend_date
            WHERE user_name='{name}' AND today_date='{date}'
            """
            curs.execute(sql)
            result = curs.fetchone()
        return result is None

    # !목표시간 설정
    def update_2(self, name, target) -> None:
        with self.conn.cursor() as curs:
            sql = f'''UPDATE attend_info SET target_time = '{target}' WHERE user_name = '{name}' '''
            curs.execute(sql)
        self.conn.commit()

    # !종료
    # 현재날짜, 하루 공부시간, 목표시간 < 하루 공부시간이면 is_achieve 1
    def update_3(self, name, today_study_time):
        with self.conn.cursor() as curs:
            sql = f'''
            SELECT target_time FROM attend_info WHERE user_name = '{name}' '''
            curs.execute(sql)
            target_time = curs.fetchone()[0]
            is_achieve = 0
            today = datetime.today().strftime("%Y-%m-%d")

            if(today_study_time > target_time):
                is_achieve = 1
            print(target_time)
            sql = f"""INSERT INTO attend_date(user_name, today_study_time, today_date, is_achieve) VALUES('{name}', 
            '{today_study_time}',  '{today}', {is_achieve})"""
            curs.execute(sql)
        self.conn.commit()

    # !종료
    # 값 수정
    def update_4(self, name, today_study_time):
        with self.conn.cursor() as curs:
            sql = f'''
            SELECT target_time FROM attend_info WHERE user_name = '{name}' '''
            curs.execute(sql)
            target_time = curs.fetchone()[0]
            is_achieve = 0
            today = datetime.today().strftime("%Y-%m-%d")

            if(today_study_time > target_time):
                is_achieve = 1

            sql = f"""
            UPDATE attend_date SET today_study_time='{today_study_time}', is_achieve = {is_achieve} WHERE user_name='{name}' AND today_date = '{today}';
            """
            curs.execute(sql)
        self.conn.commit()

    # total_study_time 업데이트
    def update_5(self, name, study_time):
        with self.conn.cursor() as curs:
            sql = f'''
            SELECT total_study_time FROM attend_info WHERE user_name ='{name}'
            '''
            curs.execute(sql)
            total_study_time = curs.fetchone()[0] + study_time
            sql = f'''
            UPDATE attend_info SET total_study_time='{total_study_time}' WHERE user_name='{name}'
            '''
            curs.execute(sql)
        self.conn.commit()

    def get_info(self, name)->str:
        with self.conn.cursor() as curs:
            sql = f'''
            SELECT today_study_time FROM attend_date WHERE user_name='{name}' and today_date='{datetime.today().strftime("%Y-%m-%d")}'
            '''
            curs.execute(sql)
            study_time = curs.fetchone()[0]
        return study_time


