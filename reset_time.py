from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from main import reset_today_attend, reset_today_rest_time, reset_today_study_time

sched = BlockingScheduler()

# Reset time values every day
@sched.scheduled_job('cron', day_of_week='mon-sun', hour=0)
def reset_time():
    #########################
    #  !공부 중인 사용자 종료 후 기록하는 코드 필요
    #########################
    reset_today_attend()
    reset_today_rest_time()
    reset_today_study_time()