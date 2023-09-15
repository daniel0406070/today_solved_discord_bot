
import datetime
from pytz import timezone


day_time= datetime.time(hour=3, minute=46, second=0, tzinfo=timezone("Asia/Seoul"))
print(day_time)