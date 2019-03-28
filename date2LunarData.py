import datetime
import lunar
from config import solarTermsData

now = datetime.datetime.now()
lunar.showMonth(now)


print(len(solarTermsData))
