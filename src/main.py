import time
import schedule
import datetime
import solveac_api

def day_fn():
    solveac_api.day_on
    print("day_on")


if __name__ == "__main__":
    schedule.every().day.at("06:00:5").do(day_fn)
    while True:
        schedule.run_pending()
        time.sleep(1)