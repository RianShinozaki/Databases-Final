import random
from datetime import datetime, timedelta

departureDay = datetime.today().strftime('%Y-%m-%d')
departureTime = datetime.strptime(departureDay, '%Y-%m-%d')
print(str(departureTime + timedelta(minutes = random.randrange(0, 1440))))