import datetime
import lunar


now=datetime.datetime(2019,6,14,22,30)
a=lunar.Lunar(now)
# a.showMonth()
print(a.date)
print(a.year8Char,a.month8Char,a.day8Char,a.twohour8Char)
print('今日时辰：%s'%a.twohour8CharList)
print('%s %s[%s]年 %s%s' % (a.lunarYearCn, a.year8Char, a.chineseYearZodiac, a.lunarMonthCn, a.lunarDayCn))
print(a.chineseZodiacClash,a.weekDayCn,a.get_starZodiac())
print('今日三合',a.zodiacMark3List,'今日六合',a.zodiacMark6)
# 今天是否是节气，下一个节气名称
print(a.todaySolarTerms,a.nextSolarTerm)
print('%i年24节气时间表%s'%(a.date.year,a.thisYearSolarTermsDic))
print(a.get_pengTaboo())
print(a.get_pengTabooLite())
print(a.get_today12Gods())