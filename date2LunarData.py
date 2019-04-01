import datetime
import lunar


now=datetime.datetime.now()
a=lunar.Lunar(now)
# a.showMonth()

print(a.year8Char,a.month8Char,a.day8Char,a.twohour8Char)
print('今日时辰：%s'%a.twohour8CharList)
print('%s %s[%s]年 %s%s'%(a.lunarYearCn,a.year8Char,a.chineseZodiac,a.lunarMonthCn,a.lunarDayCn))
print(a.weekDayCn)
# 今天是否是节气，下一个节气名称
print(a.todaySolarTerms,a.nextSolarTerm)
print('%i年24节气时间表%s'%(a.date.year,a.thisYearSolarTermsDic))