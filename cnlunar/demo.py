import datetime, cnlunar
print('a = cnlunar.Lunar(datetime.datetime(2021, 2, 7, 10, 30), godType=\'8char\')')
print('\n八字月柱与八字日柱算神煞版本')
a = cnlunar.Lunar(datetime.datetime(1985, 10, 8, 10, 30), godType='8char')  # 常规算法
# a = cnlunar.Lunar(datetime.datetime(2022, 2, 3, 10, 30), godType='8char', year8Char='beginningOfSpring')  # 八字立春切换算法
dic = {
    '日期': a.date,
    '农历数字': (a.lunarYear, a.lunarMonth, a.lunarDay, '闰' if a.isLunarLeapMonth else ''),
    '农历': '%s %s[%s]年 %s%s' % (a.lunarYearCn, a.year8Char, a.chineseYearZodiac, a.lunarMonthCn, a.lunarDayCn),
    '星期': a.weekDayCn,
    # 未增加除夕
    '今日节日': (a.get_legalHolidays(), a.get_otherHolidays(), a.get_otherLunarHolidays()),
    '八字': ' '.join([a.year8Char, a.month8Char, a.day8Char, a.twohour8Char]),
    '今日节气': a.todaySolarTerms,
    '下一节气': (a.nextSolarTerm, a.nextSolarTermDate, a.nextSolarTermYear),
    '今年节气表': a.thisYearSolarTermsDic,
    '季节': a.lunarSeason,

    '今日时辰': a.twohour8CharList,
    '时辰凶吉': a.get_twohourLuckyList(),
    '生肖冲煞': a.chineseZodiacClash,
    '星座': a.starZodiac,
    '星次': a.todayEastZodiac,

    '彭祖百忌': a.get_pengTaboo(),
    '彭祖百忌精简': a.get_pengTaboo(long=4, delimit='<br>'),
    '十二神': a.get_today12DayOfficer(),
    '廿八宿': a.get_the28Stars(),

    '今日三合': a.zodiacMark3List,
    '今日六合': a.zodiacMark6,
    '今日五行': a.get_today5Elements(),

    '纳音': a.get_nayin(),
    '九宫飞星': a.get_the9FlyStar(),
    '吉神方位': a.get_luckyGodsDirection(),
    '今日胎神': a.get_fetalGod(),
    '神煞宜忌': a.angelDemon,
    '今日吉神': a.goodGodName,
    '今日凶煞': a.badGodName,
    '宜忌等第': a.todayLevelName,
    '宜': a.goodThing,
    '忌': a.badThing,
    '时辰经络': a.meridians
}
for i in dic:
    midstr = '\t' * (2 - len(i) // 2) + ':' + '\t'
    print(i, midstr, dic[i])



# i=1
# c=0
# now = datetime.datetime(2022, 2, 4, 12, 30)
# while i <= 36600:
#     a = cnlunar.Lunar(now,godType='cnlunar')
#     now += datetime.timedelta(days=1)
#     i += 1

# print('\n农历月份与八字日柱算神煞版本，月神随月建顺行者，算出来2019年2月4日是危日，虽然与书中卷九相符，但与市面上其他日历不符，不推荐此算法，推荐用默认月柱日柱算法')
# getLunar(datetime.datetime(2019, 2, 4, 22, 30), godType='cnlunar')

# import json
# class DateEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj,datetime.datetime):
#             return obj.strftime("%Y-%m-%d %H:%M:%S")
#         else:
#             return json.JSONEncoder.default(self,obj)
# dic = getLunar(datetime.datetime(2020,11,1,22,30))
# outptJson = json.dumps(dic, cls=DateEncoder)
