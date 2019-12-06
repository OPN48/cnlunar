import datetime
import lunar


now=datetime.datetime(2019,12,6,22,30)
a=lunar.Lunar(now)
# a.showMonth()
print(a.date)
print(a.year8Char,a.month8Char,a.day8Char,a.twohour8Char)
print('今日时辰：%s'%a.twohour8CharList)
print('时辰凶吉：%s'%a.get_twohourLuckyList())

print('%s %s[%s]年 %s%s' % (a.lunarYearCn, a.year8Char, a.chineseYearZodiac, a.lunarMonthCn, a.lunarDayCn))

print(a.chineseZodiacClash,a.weekDayCn,a.get_starZodiac(),a.todayEastZodiac)
print('今日三合',a.zodiacMark3List,'今日六合',a.zodiacMark6)
print('今天是否是节气:',a.todaySolarTerms,'下一节气名称:',a.nextSolarTerm,a.thisYearSolarTermsDic[a.nextSolarTerm])
print('%i年24节气时间表 %s'%(a.date.year,a.thisYearSolarTermsDic))
print('彭祖百忌',a.get_pengTaboo())
print('彭祖百忌',a.get_pengTaboo(long=4,delimit='<br>'))
print('建除十二神', a.get_today12DayOfficer())

print('节日',a.get_legalHolidays(),a.get_otherHolidays(),a.get_otherLunarHolidays())

print('%s年%s'% (a.year8Char, a.lunarMonthCn))
print('今日五行',a.get_today5Elements())
print(a.get_the28Stars(),a.get_nayin())
print(a.get_the9FlyStar())
print(a.get_luckyGodsDirection())
print('今日胎神',a.get_fetalGod())

print(a.get_AngelDemon())
print(a.lunarSeason)