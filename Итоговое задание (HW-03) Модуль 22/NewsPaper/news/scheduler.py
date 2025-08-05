from apscheduler.schedulers.background import BackgroundScheduler
from .tasks import send_weekly_digest

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_weekly_digest, 'interval', weeks=1)
    # scheduler.add_job(send_weekly_digest, 'interval', minutes= 1)
    scheduler.start()