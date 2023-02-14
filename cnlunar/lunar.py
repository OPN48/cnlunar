# coding=UTF-8
# 1901~2100年农历数据表
# author: cuba3, github: https://github.com/opn48/pylunar
# base code by Yovey , https://www.jianshu.com/p/8dc0d7ba2c2a
# powered by Late Lee, http://www.latelee.org/python/python-yangli-to-nongli.html#comment-78
# other author:Chen Jian, http://www.cnblogs.com/chjbbs/p/5704326.html
# 数据来源: http://data.weather.gov.hk/gts/time/conversion1_text_c.htm


from datetime import datetime, timedelta
from cnlunar.config import *
from cnlunar.holidays import otherLunarHolidaysList, otherHolidaysList, legalsolarTermsHolidayDic, legalHolidaysDic, \
    legalLunarHolidaysDic
from cnlunar.solar24 import getTheYearAllSolarTermsList
from cnlunar.tools import sortCollation, rfRemove, rfAdd


class Lunar:
    def __init__(self, date, godType='8char', year8Char='year'):
        self.godType = godType
        self.year8Char = year8Char

        self.date = date
        self.twohourNum = (self.date.hour + 1) // 2
        self._upper_year = ''
        self.isLunarLeapMonth = False
        (self.lunarYear, self.lunarMonth, self.lunarDay) = self.get_lunarDateNum()
        (self.lunarYearCn, self.lunarMonthCn, self.lunarDayCn) = self.get_lunarCn()
        self.phaseOfMoon = self.getPhaseOfMoon()

        self.todaySolarTerms = self.get_todaySolarTerms()
        # 立春干支参数
        self._x = 1 if self.year8Char == 'beginningOfSpring' and self.nextSolarTermYear == self.lunarYear and self.nextSolarNum < 3 else 0

        (self.year8Char, self.month8Char, self.day8Char) = self.get_the8char()
        self.get_earthNum(), self.get_heavenNum(), self.get_season()
        self.twohour8CharList = self.get_twohour8CharList()
        self.twohour8Char = self.get_twohour8Char()
        self.get_today12DayOfficer()

        self.chineseYearZodiac = self.get_chineseYearZodiac()
        self.chineseZodiacClash = self.get_chineseZodiacClash()
        self.weekDayCn = self.get_weekDayCn()
        self.starZodiac = self.get_starZodiac()
        self.todayEastZodiac = self.get_eastZodiac()
        self.thisYearSolarTermsDic = dict(zip(SOLAR_TERMS_NAME_LIST, self.thisYearSolarTermsDateList))

        self.today28Star = self.get_the28Stars()
        self.content = ''
        self.angelDemon = self.get_AngelDemon()
        self.meridians = meridiansName[self.twohourNum % 12]

    def get_lunarYearCN(self):
        for i in str(self.lunarYear):
            self._upper_year += upperNum[int(i)]
        return self._upper_year

    def get_lunarMonthCN(self):
        # leap = (self.lunarMonth >> 4) & 0xf
        # m = self.lunarMonth & 0xf
        lunarMonth = lunarMonthNameList[(self.lunarMonth - 1) % 12]
        thisLunarMonthDays = self.monthDaysList[0]
        if self.isLunarLeapMonth:
            lunarMonth = "闰" + lunarMonth
            thisLunarMonthDays = self.monthDaysList[2]
        if thisLunarMonthDays < 30:
            self.lunarMonthLong = False
        else:
            self.lunarMonthLong = True
        s = '大' if self.lunarMonthLong else '小'
        return lunarMonth + s

    def get_lunarCn(self):
        return self.get_lunarYearCN(), self.get_lunarMonthCN(), lunarDayNameList[(self.lunarDay - 1) % 30]

    # 月相
    def getPhaseOfMoon(self):
        if self.lunarDay - int(self.lunarMonthLong) == 15:
            return '望'
        elif self.lunarDay == 1:
            return '朔'
        elif self.lunarDay in range(7, 9):
            return '上弦'
        elif self.lunarDay in range(22, 24):
            return '下弦'
        else:
            return ''

    # 生肖
    def get_chineseYearZodiac(self):
        return chineseZodiacNameList[(self.lunarYear - 4) % 12 - self._x]

    def get_chineseZodiacClash(self):
        zodiacNum = self.dayEarthNum
        zodiacClashNum = (zodiacNum + 6) % 12
        self.zodiacMark6 = chineseZodiacNameList[(25 - zodiacNum) % 12]
        self.zodiacMark3List = [chineseZodiacNameList[(zodiacNum + 4) % 12],
                                chineseZodiacNameList[(zodiacNum + 8) % 12]]
        self.zodiacWin = chineseZodiacNameList[zodiacNum]
        self.zodiacLose = chineseZodiacNameList[zodiacClashNum]
        return self.zodiacWin + '日冲' + self.zodiacLose

    # 星期
    def get_weekDayCn(self):
        '''输出当前日期中文星期几
        :return: 星期三
        '''
        return weekDay[self.date.weekday()]

    # 农历月数
    def getMonthLeapMonthLeapDays(self):
        """ 计算阴历月天数
            Arg:
                type(_cn_year) int 2018 数字年份
                type(lunarMonthNameList) int 6 数字阴历月份
            Return:
                int 30或29,该年闰月，闰月天数【
        """
        # 输入年小于1900年直接输出天数为30？？？？这个可能有点问题
        # if (_cn_year < START_YEAR):
        #     return 30
        leapMonth, leap_day, month_day = 0, 0, 0  # 闰几月，该月多少天 传入月份多少天
        tmp = lunarMonthData[self.lunarYear - START_YEAR]  # 获取16进制数据 12-1月份农历日数 0=29天 1=30天
        # 表示获取当前月份的布尔值:指定二进制1（假定真），向左移动月数-1，与当年全年月度数据合并取出2进制位作为判断
        if tmp & (1 << (self.lunarMonth - 1)):
            month_day = 30
        else:
            month_day = 29
        # 闰月
        leapMonth = (tmp >> LEAPMONTH_NUM_BIT) & 0xf
        if leapMonth:
            if (tmp & (1 << MONTH_DAY_BIT)):
                leap_day = 30
            else:
                leap_day = 29
        self.monthDaysList = [month_day, leapMonth, leap_day]
        return month_day, leapMonth, leap_day

    # # # 基础 # # #
    def get_lunarDateNum(self):
        """ 获取数字形式的农历日期
            Args:
                _date = datetime(year, month, day)
            Return:
                lunarYear, lunarMonth, lunarDay
                返回的月份，高4bit为闰月月份，低4bit为其它正常月份
        """
        self.lunarYear, self.lunarMonth, self.lunarDay = self.date.year, 1, 1
        _code_year = lunarNewYearList[self.lunarYear - START_YEAR]
        """ 获取当前日期与当年春节的差日 """
        _span_days = (self.date - datetime(self.lunarYear, ((_code_year >> 5) & 0x3), ((_code_year >> 0) & 0x1f))).days
        if (_span_days >= 0):
            """ 新年后推算日期，差日依序减月份天数，直到不足一个月，剪的次数为月数，剩余部分为日数 """
            """ 先获取闰月 """
            # 可从迭代递归修改为数学加和    待优化
            _monthDays, _leap_month, _leap_day = self.getMonthLeapMonthLeapDays()
            while _span_days >= _monthDays:
                """ 获取当前月份天数，从差日中扣除 """
                _span_days -= _monthDays
                if (self.lunarMonth == _leap_month):
                    """ 如果当月还是闰月 """
                    _monthDays = _leap_day
                    if (_span_days < _monthDays):
                        """ 指定日期在闰月中 ???"""
                        # self.lunarMonth = _leap_month
                        self.isLunarLeapMonth = True
                        break
                    """ 否则扣除闰月天数，月份加一 """
                    _span_days -= _monthDays
                self.lunarMonth += 1
                # 上一版本优化有误
                _monthDays = self.getMonthLeapMonthLeapDays()[0]
            self.lunarDay += _span_days
            return self.lunarYear, self.lunarMonth, self.lunarDay
        else:
            """ 新年前倒推去年日期 """
            self.lunarMonth = 12
            self.lunarYear -= 1
            _monthDays, _leap_month, _leap_day = self.getMonthLeapMonthLeapDays()
            while abs(_span_days) > _monthDays:
                _span_days += _monthDays
                self.lunarMonth -= 1
                if (self.lunarMonth == _leap_month):
                    _monthDays = _leap_day
                    if (abs(_span_days) <= _monthDays):  # 指定日期在闰月中
                        self.isLunarLeapMonth = True
                        # self.lunarMonth = self.lunarMonth | (_leap_month << 4)
                        break
                    _span_days += _monthDays
                _monthDays = self.getMonthLeapMonthLeapDays()[0]
            self.lunarDay += (_monthDays + _span_days)  # 从月份总数中倒扣 得到天数
            return self.lunarYear, self.lunarMonth, self.lunarDay

    # # # 24节气部分
    def getSolarTermsDateList(self, year):
        solarTermsList = getTheYearAllSolarTermsList(year)
        solarTermsDateList = []
        for i in range(0, len(solarTermsList)):
            day = solarTermsList[i]
            month = i // 2 + 1
            solarTermsDateList.append((month, day))
        return solarTermsDateList

    def getNextNum(self, findDate, solarTermsDateList):
        nextSolarNum = len(list(filter(lambda y: y <= findDate, solarTermsDateList))) % 24

        return nextSolarNum

    def get_todaySolarTerms(self):
        '''
        :return:节气
        '''
        year = self.date.year
        solarTermsDateList = self.getSolarTermsDateList(year)
        self.thisYearSolarTermsDateList = solarTermsDateList
        findDate = (self.date.month, self.date.day)
        self.nextSolarNum = self.getNextNum(findDate, solarTermsDateList)
        if findDate in solarTermsDateList:
            todaySolarTerm = SOLAR_TERMS_NAME_LIST[solarTermsDateList.index(findDate)]
        else:
            todaySolarTerm = '无'
        # 次年节气
        if findDate[0] == solarTermsDateList[-1][0] and findDate[1] >= solarTermsDateList[-1][1]:
            year += 1
            solarTermsDateList = self.getSolarTermsDateList(year)
        else:
            pass
        self.nextSolarTerm = SOLAR_TERMS_NAME_LIST[self.nextSolarNum]
        self.nextSolarTermDate = solarTermsDateList[self.nextSolarNum]
        self.nextSolarTermYear = year
        return todaySolarTerm

    # 星次
    def get_eastZodiac(self):
        todayEastZodiac = EAST_ZODIAC_LIST[(SOLAR_TERMS_NAME_LIST.index(self.nextSolarTerm) - 1) % 24 // 2]
        return todayEastZodiac

    # # # 八字部分
    def get_year8Char(self):
        # 立春年干争议算法
        str = the60HeavenlyEarth[(self.lunarYear - 4) % 60 - self._x]
        return str

    # 月八字与节气相关
    def get_month8Char(self):
        #
        # findDate = (self.date.month, self.date.day)
        # solarTermsDateList = self.getSolarTermsDateList(self.date.year)
        nextNum = self.nextSolarNum
        # 2019年正月为丙寅月
        if nextNum == 0 and self.date.month == 12:
            nextNum = 24
        apartNum = (nextNum + 1) // 2
        # (year-2019)*12+apartNum每年固定差12个月回到第N年月柱，2019小寒甲子，加上当前过了几个节气除以2+(nextNum-1)//2，减去1
        month8Char = the60HeavenlyEarth[((self.date.year - 2019) * 12 + apartNum) % 60]
        return month8Char

    def get_day8Char(self):
        apart = self.date - datetime(2019, 1, 29)
        baseNum = the60HeavenlyEarth.index('丙寅')
        # 超过23点算第二天，为防止溢出，在baseNum上操作+1
        if self.twohourNum == 12:
            baseNum += 1
        self.dayHeavenlyEarthNum = (apart.days + baseNum) % 60
        return the60HeavenlyEarth[self.dayHeavenlyEarthNum]

    def get_twohour8CharList(self):
        # 北京时间离长安时间差1小时，一天24小时横跨13个时辰,清单双循环
        begin = (the60HeavenlyEarth.index(self.day8Char) * 12) % 60
        return (the60HeavenlyEarth + the60HeavenlyEarth)[begin:begin + 13]

    def get_twohour8Char(self):
        return self.twohour8CharList[self.twohourNum % 12]

    def get_the8char(self):
        return self.get_year8Char(), self.get_month8Char(), self.get_day8Char()

    def get_earthNum(self):
        self.yearEarthNum = the12EarthlyBranches.index(self.year8Char[1])
        self.monthEarthNum = the12EarthlyBranches.index(self.month8Char[1])
        self.dayEarthNum = the12EarthlyBranches.index(self.day8Char[1])
        return self.yearEarthNum, self.monthEarthNum, self.dayEarthNum

    def get_heavenNum(self):
        self.yearHeavenNum = the10HeavenlyStems.index(self.year8Char[0])
        self.monthHeavenNum = the10HeavenlyStems.index(self.month8Char[0])
        self.dayHeavenNum = the10HeavenlyStems.index(self.day8Char[0])
        return self.yearHeavenNum, self.monthHeavenNum, self.dayHeavenNum

    # 季节
    def get_season(self):
        self.seasonType = self.monthEarthNum % 3
        self.seasonNum = ((self.monthEarthNum - 2) % 12) // 3
        self.lunarSeason = '仲季孟'[self.seasonType] + '春夏秋冬'[self.seasonNum]

    # 星座
    def get_starZodiac(self):
        return STAR_ZODIAC_NAME[len(list(filter(lambda y: y <= (self.date.month, self.date.day), STAR_ZODIAC_DATE))) % 12]

    # 节日
    def get_legalHolidays(self):
        temp = ''
        if self.todaySolarTerms in legalsolarTermsHolidayDic:
            temp += legalsolarTermsHolidayDic[self.todaySolarTerms] + ' '
        if (self.date.month, self.date.day) in legalHolidaysDic:
            temp += legalHolidaysDic[(self.date.month, self.date.day)] + ' '
        if not self.lunarMonth > 12:
            if (self.lunarMonth, self.lunarDay) in legalLunarHolidaysDic:
                temp += legalLunarHolidaysDic[(self.lunarMonth, self.lunarDay)]
        return temp.strip().replace(' ', ',')

    def get_otherHolidays(self):
        tempList, y, m, d, wn, w = [], self.date.year, self.date.month, self.date.day, self.date.isocalendar()[1], \
                                   self.date.isocalendar()[2]
        eastHolidays = {5: (2, 7, '母亲节'), 6: (3, 7, '父亲节')}
        if m in eastHolidays:
            t1dwn = datetime(y, m, 1).isocalendar()[1]
            if ((wn - t1dwn + 1), w) == (eastHolidays[m][0], eastHolidays[m][1]):
                tempList.append(eastHolidays[m][2])
        holidayDic = otherHolidaysList[m - 1]
        if d in holidayDic:
            tempList.append(holidayDic[d])
        if tempList != []:
            return ','.join(tempList)
        else:
            return ''

    def get_otherLunarHolidays(self):
        if not self.lunarMonth > 12:
            holidayDic = otherLunarHolidaysList[self.lunarMonth - 1]
            if self.lunarDay in holidayDic:
                return holidayDic[self.lunarDay]
        return ''

    # 彭祖百忌
    def get_pengTaboo(self, long=9, delimit=','):
        return pengTatooList[self.dayHeavenNum][:long] + delimit + pengTatooList[self.dayEarthNum + 10][:long]

    # 建除十二神，《淮南子》曰：正月建寅，则寅为建，卯为除，辰为满，巳为平，主生；午为定，未为执，主陷；申为破，主衡；酉为危，主杓；戍为成，主小德；亥为收，主大备；子为开，主太阳；丑为闭，主太阴。
    def get_today12DayOfficer(self):
        '''
        chinese12DayGods=['青龙','明堂','天刑','朱雀','金贵','天德','白虎','玉堂','天牢','玄武','司命','勾陈']

        '''
        if self.godType == 'cnlunar':
            # 使用农历月份与八字日柱算神煞（辨方书文字） 农历(1-12)，-1改编号，[0-11]，+2位移，% 12 防止溢出
            lmn = self.lunarMonth
            men = (lmn - 1 + 2) % 12
        else:
            # 使用八字月柱与八字日柱算神煞（辨方书配图和部分文字）
            men = self.monthEarthNum

        # thisMonthStartGodNum = (self.lunarMonth -1 + 2) % 12
        # print(str(self.lunarMonth)+'=========='+str(thisMonthStartGodNum))
        thisMonthStartGodNum = (men) % 12
        # print(str(self.monthEarthNum) + '==========' + str(thisMonthStartGodNum))
        apartNum = self.dayEarthNum - thisMonthStartGodNum
        self.today12DayOfficer = chinese12DayOfficers[apartNum % 12]
        # 青龙定位口诀：子午寻申位，丑未戌上亲；寅申居子中，卯酉起于寅；辰戌龙位上，巳亥午中寻。
        # [申戌子寅辰午]
        # 十二神凶吉口诀：道远几时通达，路遥何日还乡
        # 辶为吉神(0, 1, 4, 5, 7, 10)
        # 为黄道吉日
        eclipticGodNum = (self.dayEarthNum - [8, 10, 0, 2, 4, 6, 8, 10, 0, 2, 4, 6][men]) % 12
        self.today12DayGod = chinese12DayGods[eclipticGodNum % 12]
        dayName = '黄道日' if eclipticGodNum in (0, 1, 4, 5, 7, 10) else '黑道日'
        return self.today12DayOfficer, self.today12DayGod, dayName

    # 八字与五行
    def get_the28Stars(self):
        apart = self.date - datetime(2019, 1, 17)
        return the28StarsList[apart.days % 28]

    def get_nayin(self):
        return theHalf60HeavenlyEarth5ElementsList[the60HeavenlyEarth.index(self.day8Char) // 2]

    def get_today5Elements(self):
        nayin = self.get_nayin()
        tempList = ['天干', self.day8Char[0],
                    '属' + the10HeavenlyStems5ElementsList[self.dayHeavenNum],
                    '地支', self.day8Char[1],
                    '属' + the12EarthlyBranches5ElementsList[self.dayEarthNum],
                    '纳音', nayin[-1], '属' + nayin[-1],
                    '廿八宿', self.today28Star[0], '宿',
                    '十二神', self.today12DayOfficer, '日'
                    ]
        return tempList

    def get_the9FlyStar(self):
        apartNum = (self.date - datetime(2019, 1, 17)).days
        startNumList = [7, 3, 5, 6, 8, 1, 2, 4, 9]
        flyStarList = [str((i - 1 - apartNum) % 9 + 1) for i in startNumList]
        return ''.join(flyStarList)

    def get_luckyGodsDirection(self):
        todayNum = self.dayHeavenNum
        direction = [
            '喜神' + directionList[chinese8Trigrams.index(luckyGodDirection[todayNum])],
            '财神' + directionList[chinese8Trigrams.index(wealthGodDirection[todayNum])],
            '福神' + directionList[chinese8Trigrams.index(mascotGodDirection[todayNum])],
            '阳贵' + directionList[chinese8Trigrams.index(sunNobleDirection[todayNum])],
            '阴贵' + directionList[chinese8Trigrams.index(moonNobleDirection[todayNum])],
        ]
        return direction

    def get_fetalGod(self):
        return fetalGodList[the60HeavenlyEarth.index(self.day8Char)]

    # 每日时辰凶吉
    def get_twohourLuckyList(self):
        def tmp2List(tmp):
            return ['凶' if tmp & (2 ** (12 - i)) > 0 else '吉' for i in range(1, 13)]

        todayNum = self.dayHeavenlyEarthNum
        tomorrowNum = (self.dayHeavenlyEarthNum + 1) % 60
        outputList = (tmp2List(twohourLuckyTimeList[todayNum]) + tmp2List(twohourLuckyTimeList[tomorrowNum]))
        return outputList[:13]

    # 宜忌等第表 计算凶吉
    def getTodayThingLevel(self):
        '''
        :return thingLevel
        '''
        badGodDic = {
            '平日': [
                ('亥', ['相日', '时德', '六合'], 0),
                ('巳', ['相日', '六合', '月刑'], 1),
                ('申', ['相日', '月害'], 2),
                ('寅', ['相日', '月害', '月刑'], 3),
                ('卯午酉', ['天吏'], 3),
                ('辰戌丑未', ['月煞'], 4),
                ('子', ['天吏', '月刑'], 4)
            ],
            '收日': [
                ('寅申', ['长生', '六合', '劫煞'], 0),
                ('巳亥', ['长生', '劫煞'], 2),
                ('辰未', ['月害'], 2),
                ('子午酉', ['大时'], 3),
                ('丑戌', ['月刑'], 3),
                ('卯', ['大时'], 4),
            ],
            '闭日': [
                ('子午卯酉', ['王日'], 3),
                ('辰戌丑未', ['官日', '天吏'], 3),
                ('寅申巳亥', ['月煞'], 4)
            ],
            '劫煞': [
                # ('寅申', ['长生', '六合', '收日'], 0
                ('寅申', ['长生', '六合'], 0),
                ('辰戌丑未', ['除日', '相日'], 1),
                # ('巳亥', ['长生', '月害', '收日'], 2)
                ('巳亥', ['长生', '月害'], 2),
                ('子午卯酉', ['执日'], 3)
            ],
            '灾煞': [
                ('寅申巳亥', ['开日'], 1),
                ('辰戌丑未', ['满日', '民日'], 2),
                ('子午', ['月破'], 4),
                ('卯酉', ['月破', '月厌'], 5)
            ],
            '月煞': [
                ('卯酉', ['六合', '危日'], 1),
                ('子午', ['月害', '危日'], 3),
                # ('寅申巳亥', ['闭日'], 4),
                # ('辰戌丑未', ['平日'], 4)
            ],
            '月刑': [
                ('巳', ['平日', '六合', '相日'], 1),
                ('寅', ['相日', '月害', '平日'], 3),
                ('辰酉亥', ['建日'], 3),
                # ('丑戌', ['收日'], 3),
                ('子', ['平日', '天吏'], 4),
                ('卯', ['收日', '大时', '天破'], 4),
                ('未申', ['月破'], 4),
                ('午', ['月建', '月厌', '德大会'], 4)
            ],
            '月害': [
                ('卯酉', ['守日', '除日'], 2),
                ('丑未', ['执日', '大时'], 2),
                ('巳亥', ['长生', '劫煞'], 2),
                ('申', ['相日', '平日'], 2),
                ('子午', ['月煞'], 3),
                ('辰戌', ['官日', '闭日', '天吏'], 3),
                ('寅', ['相日', '平日', '月刑'], 3)
            ],
            '月厌': [
                ('寅申', ['成日'], 2),
                ('丑未', ['开日'], 2),
                ('辰戌', ['定日'], 3),
                ('已亥', ['满日'], 3),
                ('子', ['月建', '德大会'], 4),
                ('午', ['月建', '月刑', '德大会'], 4),
                ('卯酉', ['月破', '灾煞'], 5)
            ],
            '大时': [
                ('寅申已亥', ['除日', '官日'], 0),
                ('辰戌', ['执日', '六合'], 0),
                ('丑未', ['执日', '月害'], 2),
                ('子午酉', ['收日'], 3),
                ('卯', ['收日', '月刑'], 4)
            ],
            '天吏': [
                ('寅申已亥', ['危日'], 2),
                ('辰戌丑未', ['闭日'], 3),
                ('卯午酉', ['平日'], 3),
                ('子', ['平日', '月刑'], 4),
            ]
        }
        todayAllGodName = self.goodGodName + self.badGodName + [self.today12DayOfficer + '日']
        l = -1
        for gnoItem in todayAllGodName:
            if gnoItem in badGodDic:
                for item in badGodDic[gnoItem]:
                    if self.month8Char[1] in item[0]:
                        for godname in item[1]:
                            if godname in todayAllGodName and item[2] > l:
                                l = item[2]
                                break
        # 今日宜忌等第
        levelDic = {0: '上：吉足胜凶，从宜不从忌。', 1: '上次：吉足抵凶，遇德从宜不从忌，不遇从宜亦从忌。', 2: '中：吉不抵凶，遇德从宜不从忌，不遇从忌不从宜。', 3: '中次：凶胜于吉，遇德从宜亦从忌，不遇从忌不从宜。', 4: '下:凶又逢凶，遇德从忌不从宜，不遇诸事皆忌。', 5: '下下：凶叠大凶，遇德亦诸事皆忌。（卯酉月，灾煞遇月破、月厌，月厌遇灾煞、月破）', -1: '无'}
        self.todayLevel = l
        self.todayLevelName = levelDic[l]
        thingLevelDic = {0: '从宜不从忌', 1: '从宜亦从忌', 2: '从忌不从宜', 3: '诸事皆忌'}
        self.isDe = False
        for i in self.goodGodName:
            if i in ['岁德', '岁德合', '月德', '月德合', '天德', '天德合']:
                self.isDe = True
                break
        # 下下：凶叠大凶，遇德亦诸事皆忌；卯酉月 灾煞遇 月破、月厌  月厌遇灾煞、月破
        if l == 5:
            thingLevel = 3

        # 下：凶又逢凶，遇德从忌不从宜，不遇诸事皆忌；
        elif l == 4:
            if self.isDe:
                thingLevel = 2
            else:
                thingLevel = 3
        # 中次：凶胜于吉，遇德从宜亦从忌，不遇从忌不从宜；
        elif l == 3:
            if self.isDe:
                thingLevel = 1
            else:
                thingLevel = 2
        # 中：吉不抵凶，遇德从宜不从忌，不遇从忌不从宜；
        elif l == 2:
            if self.isDe:
                thingLevel = 0
            else:
                thingLevel = 2
        # 上次：吉足抵凶，遇德从宜不从忌，不遇从宜亦从忌；
        elif l == 1:
            if self.isDe:
                thingLevel = 0
            else:
                thingLevel = 1
        # 上：吉足胜凶，从宜不从忌;
        elif l == 0:
            thingLevel = 0
        # 无，例外 从宜不从忌
        else:
            thingLevel = 1
        self.thingLevelName = thingLevelDic[thingLevel]
        return thingLevel

    def get_AngelDemon(self):
        '''
        the10HeavenlyStems =['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        the12EarthlyBranches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        相冲+6
        四绝日：一切用事皆忌之，立春，立夏，立秋，立冬前一日。忌出行、赴任、嫁娶、进人、迁移、开市、立券、祭祀
        四离日：春分、秋分、夏至、冬至前一天。日值四离，大事勿用
        杨公13忌日：忌开张、动工、嫁娶、签订合同
        红纱日、正红纱日：四孟金鸡（酉）四仲蛇（巳），四季丑日是红纱，惟有孟仲合吉用 ，季月逢之俱不佳（正红纱日）
        凤凰日、麒麟日：凤凰压朱雀，麒麟制白虎，克制朱雀白虎中效果。春井，夏尾，秋牛，冬壁，是麒麟日，春危，夏昴，秋胃，冬毕是凤凰日
        月德、月德合:申子辰三合，阳水为壬，月德合丁；巳酉丑三合，阳金为庚，月德合乙；寅午戌三合，阳火为丙，月德合辛；亥卯未三合，阳木为甲，月德合己
        天德、天德合:《子平赋》说：印绶得同天德，官刑不至，至老无灾.
        岁德、岁德合:《协纪辨方书·义例一·岁德》：曾门经曰：岁德者，岁中德神也。https://www.jianshu.com/p/ec0432f31060
        月恩:正月逢丙是月恩，二月见丁三庚真，四月己上五月戊，六辛七壬八癸成，九月庚上十月乙，冬月甲上腊月辛。
        天恩:四季何时是天恩，甲子乙丑丙寅建。丁卯戊辰兼己卯，庚辰辛巳壬午言，癸未隔求己酉日，庚戌辛亥亦同联，壬子癸丑无差误，此是天恩吉日传
        '''

        gbDic = {'goodName': [], 'badName': [], 'goodThing': officerThings[self.today12DayOfficer][0],
                 'badThing': officerThings[self.today12DayOfficer][1]}
        mrY13 = [(1, 13), (2, 11), (3, 9), (4, 7), (5, 5), (6, 2), (7, 1), (7, 29), (8, 27), (9, 25), (10, 23),
                 (11, 21), (12, 19)]
        tomorrow = self.date + timedelta(days=1)
        tmd = (tomorrow.month, tomorrow.day)
        t4l = [self.thisYearSolarTermsDic[i] for i in ['春分', '夏至', '秋分', '冬至']]
        t4j = [self.thisYearSolarTermsDic[i] for i in ['立春', '立夏', '立秋', '立冬']]
        twys = t4j[len(list(filter(lambda y: y < tmd, t4j))) % 4]
        s = self.today28Star
        o = self.today12DayOfficer
        d = self.day8Char
        den = self.dayEarthNum
        dhen = self.dayHeavenlyEarthNum
        sn = self.seasonNum  # 季节
        # st=self.seasonType
        yhn = self.yearHeavenNum
        yen = self.yearEarthNum
        ldn = self.lunarDay
        lmn = self.lunarMonth
        if self.godType == 'cnlunar':
            # 使用农历月份与八字日柱算神煞（辨方书文字） 农历(1-12)，-1改编号，[0-11]，+2位移，% 12 防止溢出
            men = (lmn - 1 + 2) % 12
        else:
            # 使用八字月柱与八字日柱算神煞（辨方书配图和部分文字）
            men = self.monthEarthNum

        # item参数规则，（name,当日判断结果,判断规则,宜事,忌事）
        for i in day8CharThing:
            if i in d:
                gbDic['goodThing'] += day8CharThing[i][0]
                gbDic['badThing'] += day8CharThing[i][1]
        # 插入卷十一拆解后遗留内容
        # 节气间差类
        # [('小寒', 0), ('大寒', 1), ('立春', 2), ('雨水', 3), ('惊蛰', 4), ('春分', 5), ('清明', 6), ('谷雨', 7), ('立夏', 8), ('小满', 9), ('芒种', 10), ('夏至', 11), ('小暑', 12), ('大暑', 13), ('立秋', 14), ('处暑', 15), ('白露', 16), ('秋分', 17), ('寒露', 18), ('霜降', 19), ('立冬', 20), ('小雪', 21), ('大雪', 22), ('冬至', 23)]
        # 雨水后立夏前执日、危日、收日 宜 取鱼
        if self.nextSolarNum in range(4, 9) and o in ['执', '危', '收']:
            gbDic['goodThing'] = rfAdd(gbDic['goodThing'], ['取鱼'])
        # 霜降后立春前执日、危日、收日 宜 畋猎
        if self.nextSolarNum in range(20, 24) and self.nextSolarNum in range(0, 3) and o in ['执', '危', '收']:
            gbDic['goodThing'] = rfAdd(gbDic['goodThing'], ['畋猎'])
        # 立冬后立春前危日 午日 申日 宜 伐木
        if self.nextSolarNum in range(21, 24) and self.nextSolarNum in range(0, 3) and (o in ['危'] or d in ['午', '申']):
            gbDic['goodThing'] = rfAdd(gbDic['goodThing'], ['伐木'])
        #   每月一日 六日 十五 十九日 二十一日 二十三日 忌 整手足甲
        if ldn in [1, 6, 15, 19, 21, 23]:
            gbDic['badThing'] = rfAdd(gbDic['badThing'], ['整手足甲'])
        # 每月十二日 十五日 忌 整容剃头
        if ldn in [12, 15]:
            gbDic['badThing'] = rfAdd(gbDic['badThing'], ['整容', '剃头'])
        # 每月十五日 朔弦望月 忌 求医疗病
        if ldn in [15] or self.phaseOfMoon != '':
            gbDic['badThing'] = rfAdd(gbDic['badThing'], ['求医疗病'])

        # 由于正月建寅，men参数使用排序是从子开始，所以对照书籍需要将循环八字列向右移两位，也就是映射正月的是在第三个字
        angel = [
            ('岁德', '甲庚丙壬戊甲庚丙壬戊'[yhn], d, ['修造', '嫁娶', '纳采', '搬移', '入宅'], []),
            # 岁德、岁德合：年天干对日天干['修造','动土','嫁娶','纳采','移徙','入宅','百事皆宜'] 天干相合+5  20190206
            ('岁德合', '己乙辛丁癸己乙辛丁癸'[yhn], d, ['修造', '赴任', '嫁娶', '纳采', '搬移', '入宅', '出行'], []),  # 修营、起土，上官。嫁娶、远行，参谒
            ('月德', '壬庚丙甲壬庚丙甲壬庚丙甲'[men], d[0],
             ['祭祀', '祈福', '求嗣', '上册', '上表章', '颁诏', '覃恩', '施恩', '招贤', '举正直', '恤孤茕', '宣政事', '雪冤', '庆赐', '宴会', '出行',
              '安抚边境', '选将', '出师', '上官', '临政', '结婚姻', '纳采', '嫁娶', '搬移', '解除', '求医疗病', '裁制', '营建', '缮城郭', '修造', '竖柱上梁',
              '修仓库', '栽种', '牧养', '纳畜', '安葬'], ['畋猎', '取鱼']),
            # 月德20190208《天宝历》曰：“月德者，月之德神也。取土、修营宜向其方，宴乐、上官利用其日。
            ('月德合', '丁乙辛己丁乙辛己丁乙辛己'[men], d[0],
             ['祭祀', '祈福', '求嗣', '上册', '上表章', '颁诏', '覃恩', '施恩', '招贤', '举正直', '恤孤茕', '宣政事', '雪冤', '庆赐', '宴会', '出行',
              '安抚边境', '选将', '出师', '上官', '临政', '结婚姻', '纳采', '嫁娶', '搬移', '解除', '求医疗病', '裁制', '营建', '缮城郭', '修造', '竖柱上梁',
              '修仓库', '栽种', '牧养', '纳畜', '安葬'], ['畋猎', '取鱼']),
            ('天德', '巳庚丁申壬辛亥甲癸寅丙乙'[men], d,
             ['祭祀', '祈福', '求嗣', '上册', '上表章', '颁诏', '覃恩', '施恩', '招贤', '举正直', '恤孤茕', '宣政事', '雪冤', '庆赐', '宴会', '出行',
              '安抚边境', '选将', '出师', '上官', '临政', '结婚姻', '纳采', '嫁娶', '搬移', '解除', '求医疗病', '裁制', '营建', '缮城郭', '修造', '竖柱上梁',
              '修仓库', '栽种', '牧养', '纳畜', '安葬'], ['畋猎', '取鱼']),  # 天德'巳庚丁申壬辛亥甲癸寅丙乙'天德合'申乙壬巳丁丙寅己戊亥辛庚'
            ('天德合', '空乙壬空丁丙空己戊空辛庚'[men], d,
             ['祭祀', '祈福', '求嗣', '上册', '上表章', '颁诏', '覃恩', '施恩', '招贤', '举正直', '恤孤茕', '宣政事', '雪冤', '庆赐', '宴会', '出行',
              '安抚边境', '选将', '出师', '上官', '临政', '结婚姻', '纳采', '嫁娶', '搬移', '解除', '求医疗病', '裁制', '营建', '缮城郭', '修造', '竖柱上梁',
              '修仓库', '栽种', '牧养', '纳畜', '安葬'], ['畋猎', '取鱼']),
            ('凤凰日', s[0], '危昴胃毕'[sn], ['嫁娶'], []),
            ('麒麟日', s[0], '井尾牛壁'[sn], ['嫁娶'], []),  # 凤凰日、麒麟日（麒麟日测试日期2019.03.07）

            ('三合', (den - men) % 4 == 0, [True],
             ['庆赐', '宴会', '结婚姻', '纳采', '嫁娶', '进人口', '裁制', '修宫室', '缮城郭', '修造', '竖柱上梁', '修仓库', '经络', '酝酿', '立券交易', '纳财',
              '安碓硙', '纳畜'], []),  # 三合数在地支上相差4个顺位
            ('四相', d[0], ('丙丁', '戊己', '壬癸', '甲乙')[sn],
             ['祭祀', '祈福', '求嗣', '施恩', '举正直', '庆赐', '宴会', '出行', '上官', '临政', '结婚姻', '纳采', '搬移', '解除', '求医疗病', '裁制', '修宫室',
              '缮城郭', '修造', '竖柱上梁', '纳财', '开仓', '栽种', '牧养'], []),
            # 《总要历》曰：“四相者，四时王相之辰也。其日宜修营、起工、养育，生财、栽植、种莳、移徙、远行，曰：“春丙丁，夏戊己，秋壬癸，冬甲乙。
            ('五合', d[1], '寅卯', ['宴会', '结婚姻', '立券交易'], []),
            ('五富', '巳申亥寅巳申亥寅巳申亥寅'[men], d, ['经络', '酝酿', '开市', '立券交易', '纳财', '开仓', '栽种', '牧养', '纳畜'], []),
            ('六合', '丑子亥戌酉申未午巳辰卯寅'[men], d, ['宴会', '结婚姻', '嫁娶', '进人口', '经络', '酝酿', '立券交易', '纳财', '纳畜', '安葬'], []),
            ('六仪', '午巳辰卯寅丑子亥戌酉申未'[men], d, ['临政'], []),  # 厌对招摇

            ('不将', d, bujiang[men], ['嫁娶'], []),
            ('时德', '午辰子寅'[sn], d[1],
             ['祭祀', '祈福', '求嗣', '施恩', '举正直', '庆赐', '宴会', '出行', '上官', '临政', '结婚姻', '纳采', '搬移', '解除', '求医疗病', '裁制', '修宫室',
              '缮城郭', '修造', '竖柱上梁', '纳财', '开仓', '栽种', '牧养'], []),  # 时德:春午 夏辰 秋子 冬寅 20190204
            ('大葬', d, '壬申癸酉壬午甲申乙酉丙申丁酉壬寅丙午己酉庚申辛酉', ['安葬'], []),
            ('鸣吠', d, '庚午壬申癸酉壬午甲申乙酉己酉丙申丁酉壬寅丙午庚寅庚申辛酉', ['破土', '安葬'], []),
            ('小葬', d, '庚午壬辰甲辰乙巳甲寅丙辰庚寅', ['安葬'], []),
            # ('鸣吠对', d, '丙寅丁卯丙子辛卯甲午庚子癸卯壬子甲寅乙卯', ['安葬']),
            ('鸣吠对', d, '丙寅丁卯丙子辛卯甲午庚子癸卯壬子甲寅乙卯', ['破土', '启攒'], []),  # （改）
            ('不守塚', d, '庚午辛未壬申癸酉戊寅己卯壬午癸未甲申乙酉丁未甲午乙未丙申丁酉壬寅癸卯丙午戊申己酉庚申辛酉', ['破土'], []),
            # 《钦定协纪辨方书 卷五》《历例》 王日、官日、守日、相日、民日
            ('王日', '寅巳申亥'[sn], d[1],
             ['颁诏', '覃恩', '施恩', '招贤', '举正直', '恤孤茕', '宣政事', '雪冤', '庆赐', '宴会', '出行', '安抚边境', '选将', '上官', '临政', '裁制'], []),
            ('官日', '卯午酉子'[sn], d[1], ['上官', '临政'], []),
            ('守日', '酉子卯午'[sn], d[1], ['安抚边境', '上官', '临政'], []),
            ('相日', '巳申亥寅'[sn], d[1], ['上官', '临政'], []),
            ('民日', '午酉子卯'[sn], d[1], ['宴会', '结婚姻', '纳采', '进人口', '搬移', '开市', '立券交易', '纳财', '栽种', '牧养', '纳畜'], []),
            ('临日', '辰酉午亥申丑戌卯子巳寅未'[men], d, ['上册', '上表章', '上官', '临政'], []),  # 正月午日、二月亥日、三月申日、四月丑日等为临日
            ('天贵', d[0], ('甲乙', '丙丁', '庚辛', '壬癸')[sn], [], []),  # 20190216
            ('天喜', '申酉戌亥子丑寅卯辰巳午未'[men], d[1], ['施恩', '举正直', '庆赐', '宴会', '出行', '上官', '临政', '结婚姻', '纳采', '嫁娶'], []),
            ('天富', '寅卯辰巳午未申酉戌亥子丑'[men], d, ['安葬', '修仓库'], []),
            ('天恩', dhen % 15 < 5 and dhen // 15 != 2, [True], ['覃恩', '恤孤茕', '布政事', '雪冤', '庆赐', '宴会'], []),
            # ('月恩', '甲辛丙丁庚己戊辛壬癸庚乙'[men], d, ['营造', '婚姻', '移徙', '祭祀', '上官', '纳财', '动土']),#《五行论》曰：“月恩者，阳建所生之干也，子母相从谓之月恩。其日宜营造，婚姻、移徙，祭祀，上官，纳财。”
            ('月恩', '甲辛丙丁庚己戊辛壬癸庚乙'[men], d,
             ['祭祀', '祈福', '求嗣', '施恩', '举正直', '庆赐', '宴会', '出行', '上官', '临政', '结婚姻', '纳采', '搬移', '解除', '求医疗病', '裁制', '修宫室',
              '缮城郭', '修造', '竖柱上梁', '纳财', '开仓', '栽种', '牧养'], []),
            ('天赦', ['甲子', '甲子', '戊寅', '戊寅', '戊寅', '甲午', '甲午', '甲午', '戊申', '戊申', '戊申', '甲子'][men], d,
             ['祭祀', '祈福', '求嗣', '上册', '上表章', '颁诏', '覃恩', '施恩', '招贤', '举正直', '恤孤茕', '宣政事', '雪冤', '庆赐', '宴会', '出行',
              '安抚边境', '选将', '上官', '临政', '结婚姻', '纳采', '嫁娶', '搬移', '解除', '求医疗病', '裁制', '营建', '缮城郭', '修造', '竖柱上梁', '修仓库',
              '栽种', '牧养', '纳畜', '安葬'], ['畋猎', '取鱼']),
            ('天愿', ['甲子', '癸未', '甲午', '甲戌', '乙酉', '丙子', '丁丑', '戊午', '甲寅', '丙辰', '辛卯', '戊辰'][men], d,
             ['祭祀', '祈福', '求嗣', '上册', '上表章', '颁诏', '覃恩', '施恩', '招贤', '举正直', '恤孤茕', '宣政事', '雪冤', '庆赐', '宴会', '出行',
              '安抚边境', '选将', '上官', '临政', '结婚姻', '纳采', '嫁娶', '进人口', '搬移', '裁制', '营建', '缮城郭', '修造', '竖柱上梁', '修仓库', '经络',
              '酝酿', '开市', '立券交易', '纳财', '栽种', '牧养', '纳畜', '安葬'], []),  # 天愿日，以月之干支为依据，择与之和合之日为是，故为月之喜神
            ('天成', '卯巳未酉亥丑卯巳未酉亥丑'[men], d, [], []),
            ('天官', '午申戌子寅辰午申戌子寅辰'[men], d, [], []),
            ('天医', '亥子丑寅卯辰巳午未申酉戌'[men], d, ['求医疗病'], []),  # 《总要历》曰：“天医者，人之巫医。其日宜请药，避病、寻巫、祷祀。
            ('天马', '寅辰午申戌子寅辰午申戌子'[men], d, ['出行', '搬移'], []),  # （改）
            ('驿马', '寅亥申巳寅亥申巳寅亥申巳'[men], d, ['出行', '搬移'], []),
            ('天财', '子寅辰午申戌子寅辰午申戌'[men], d, [], []),
            ('福生', '寅申酉卯戌辰亥巳子午丑未'[men], d, ['祭祀', '祈福'], []),
            ('福厚', '寅巳申亥'[sn], d, [], []),
            ('福德', '寅卯辰巳午未申酉戌亥子丑'[men], d, ['上册', '上表章', '庆赐', '宴会', '修宫室', '缮城郭'], []),
            ('天巫', '寅卯辰巳午未申酉戌亥子丑'[men], d, ['求医疗病'], []),

            ('地财', '丑卯巳未酉亥丑卯巳未酉亥'[men], d, [], []),
            ('月财', '酉亥午巳巳未酉亥午巳巳未'[men], d, [], []),
            # ('月空', '丙甲壬庚丙甲壬庚丙甲壬庚'[men], d, ['上书', '陈策', '造床', '修屋', '动土']),#《天宝历》曰：“月中之阳辰也。所理之日宜设筹谋。陈计策。
            ('月空', '丙甲壬庚丙甲壬庚丙甲壬庚'[men], d, ['上表章'], []),  # 《天宝历》曰：“月中之阳辰也。所理之日宜设筹谋。陈计策。#（改）
            ('母仓', d[1], ('亥子', '寅卯', '辰丑戌未', '申酉')[sn], ['纳财', '栽种', '牧养', '纳畜'], []),
            ('明星', '辰午甲戌子寅辰午甲戌子寅'[men], d, ['赴任', '诉讼', '安葬'], []),
            ('圣心', '辰戌亥巳子午丑未寅申卯酉'[men], d, ['祭祀', '祈福'], []),
            ('禄库', '寅卯辰巳午未申酉戌亥子丑'[men], d, ['纳财'], []),

            ('吉庆', '未子酉寅亥辰丑午卯申巳戌'[men], d, [], []),
            ('阴德', '丑亥酉未巳卯丑亥酉未巳卯'[men], d, ['恤孤茕', '雪冤'], []),
            ('活曜', '卯申巳戌未子酉寅亥辰丑午'[men], d, [], []),
            ('除神', d[1], '申酉', ['解除', '沐浴', '整容', '剃头', '整手足甲', '求医疗病', '扫舍宇'], []),  # 五离
            ('解神', '午午申申戌戌子子寅寅辰辰'[men], d, ['上表章', '解除', '沐浴', '整容', '剃头', '整手足甲', '求医疗病'], []),
            ('生气', '戌亥子丑寅卯辰巳午未申酉'[men], d, [], ['伐木', '畋猎', '取鱼']),
            ('普护', '丑卯申寅酉卯戌辰亥巳子午'[men], d, ['祭祀', '祈福'], []),
            ('益后', '巳亥子午丑未寅申卯酉辰戌'[men], d, ['祭祀', '祈福', '求嗣'], []),
            ('续世', '午子丑未寅申卯酉辰戌巳亥'[men], d, ['祭祀', '祈福', '求嗣'], []),
            ('要安', '未丑寅申卯酉辰戌巳亥午子'[men], d, [], []),
            ('天后', '寅亥申巳寅亥申巳寅亥申巳'[men], d, ['求医疗病'], []),
            ('天仓', '辰卯寅丑子亥戌酉申未午巳'[men], d, ['进人口', '纳财', '纳畜'], []),
            # 《总要历》曰:天仓者,天库之神也。其日可以修仓库、受赏赐、纳财、牧养。《历例》曰:天仓者,正月起寅,逆行十二辰。
            ('敬安', '子午未丑申寅酉卯戌辰亥巳'[men], d, [], []),  # 恭顺之神当值
            ('玉宇', '申寅卯酉辰戌巳亥午子未丑'[men], d, [], []),
            ('金堂', '酉卯辰戌巳亥午子未丑申寅'[men], d, [], []),
            ('吉期', '丑寅卯辰巳午未申酉戌亥子'[men], d, ['施恩', '举正直', '出行', '上官', '临政'], []),
            ('小时', '子丑寅卯辰巳午未申酉戌亥'[men], d, [], []),
            ('兵福', '子丑寅卯辰巳午未申酉戌亥'[men], d, ['安抚边境', '选将', '出师'], []),
            ('兵宝', '丑寅卯辰巳午未申酉戌亥子'[men], d, ['安抚边境', '选将', '出师'], []),
            ('兵吉', d[1],
             ['寅卯辰巳', '丑寅卯辰', '子丑寅卯', '亥子丑寅', '戌亥子丑', '酉戌亥子', '申酉戌亥', '未申酉戌', '午未申酉', '巳午未申', '辰巳午未', '卯辰巳午'][men],
             ['安抚边境', '选将', '出师'], []),
        ]
        demon = [
            ('岁破', den == (yen + 6) % 12, [True], [], ['修造', '搬移', '嫁娶', '出行']),
            # 《广圣历》曰：“岁破者，太岁所冲之辰也。其地不可兴造、移徙，嫁娶、远行，犯者主损财物及害家长，惟战伐向之吉。
            ('天罡', '卯戌巳子未寅酉辰亥午丑申'[men], d, [], ['安葬']),
            ('河魁', '酉辰亥午丑申卯戌巳子未寅'[men], d, [], ['安葬']),
            ('死神', '卯辰巳午未申酉戌亥子丑寅'[men], d, [], ['安抚边境', '选将', '出师', '进人口', '解除', '求医疗病', '修置产室', '栽种', '牧养', '纳畜']),
            # ('勾绞', '酉辰亥午丑申卯戌巳子未寅'[men], d, [], []),
            ('死气', '辰巳午未申酉戌亥子丑寅卯'[men], d, [], ['安抚边境', '选将', '出师', '解除', '求医疗病', '修置产室', '栽种']),
            ('官符', '辰巳午未申酉戌亥子丑寅卯'[men], d, [], ['上表章', '上册']),
            ('月建', '子丑寅卯辰巳午未申酉戌亥'[men], d, [],
             ['祈福', '求嗣', '上册', '上表章', '结婚姻', '纳采', '解除', '整容', '剃头', '整手足甲', '求医疗病', '营建', '修宫室', '缮城郭', '修造', '竖柱上梁',
              '修仓库', '开仓', '修置产室', '破屋坏垣', '伐木', '栽种', '破土', '安葬', '启攒']),
            ('月破', '午未申酉戌亥子丑寅卯辰巳'[men], d, ['破屋坏垣'],
             ['祈福', '求嗣', '上册', '上表章', '颁诏', '施恩', '招贤', '举正直', '宣政事', '布政事', '庆赐', '宴会', '冠带', '出行', '安抚边境', '选将',
              '出师', '上官', '临政', '结婚姻', '纳采', '嫁娶', '进人口', '搬移', '安床', '整容', '剃头', '整手足甲', '裁制', '营建', '修宫室', '缮城郭',
              '筑堤防', '修造', '竖柱上梁', '修仓库', '鼓铸', '经络', '酝酿', '开市', '立券交易', '纳财', '开仓', '修置产室', '开渠', '穿井', '安碓硙', '塞穴',
              '补垣', '修饰垣墙', '伐木', '栽种', '牧养', '纳畜', '破土', '安葬', '启攒']),
            ('月煞', '未辰丑戌未辰丑戌未辰丑戌'[men], d, [],
             ['祈福', '求嗣', '上册', '上表章', '颁诏', '施恩', '招贤', '举正直', '宣政事', '布政事', '庆赐', '宴会', '冠带', '出行', '安抚边境', '选将',
              '出师', '上官', '临政', '结婚姻', '纳采', '嫁娶', '进人口', '搬移', '安床', '解除', '整容', '剃头', '整手足甲', '求医疗病', '裁制', '营建',
              '修宫室', '缮城郭', '筑堤防', '修造', '竖柱上梁', '修仓库', '鼓铸', '经络', '酝酿', '开市', '立券交易', '纳财', '开仓', '修置产室', '开渠', '穿井',
              '安碓硙', '塞穴', '补垣', '修饰垣墙', '破屋坏垣', '栽种', '牧养', '纳畜', '安葬']),
            ('月害', '未午巳辰卯寅丑子亥戌酉申'[men], d, [],
             ['祈福', '求嗣', '上册', '上表章', '庆赐', '宴会', '安抚边境', '选将', '出师', '上官', '纳采', '嫁娶', '进人口', '求医疗病', '修仓库', '经络',
              '酝酿', '开市', '立券交易', '纳财', '开仓', '修置产室', '牧养', '纳畜', '破土', '安葬', '启攒']),
            ('月刑', '卯戌巳子辰申午丑寅酉未亥'[men], d, [],
             ['祈福', '求嗣', '上册', '上表章', '颁诏', '施恩', '招贤', '举正直', '宣政事', '布政事', '庆赐', '宴会', '冠带', '出行', '安抚边境', '选将',
              '出师', '上官', '临政', '结婚姻', '纳采', '嫁娶', '进人口', '搬移', '安床', '解除', '整容', '剃头', '整手足甲', '求医疗病', '裁制', '营建',
              '修宫室', '缮城郭', '筑堤防', '修造', '竖柱上梁', '修仓库', '鼓铸', '经络', '酝酿', '开市', '立券交易', '纳财', '开仓', '修置产室', '开渠', '穿井',
              '安碓硙', '塞穴', '补垣', '修饰垣墙', '破屋坏垣', '栽种', '牧养', '纳畜', '破土', '安葬', '启攒']),
            ('月厌', '子亥戌酉申未午巳辰卯寅丑'[men], d, [],
             ['祈福', '求嗣', '上册', '上表章', '颁诏', '施恩', '招贤', '举正直', '宣政事', '布政事', '庆赐', '宴会', '冠带', '出行', '安抚边境', '选将',
              '出师', '上官', '临政', '结婚姻', '纳采', '嫁娶', '进人口', '搬移', '远回', '安床', '解除', '整容', '剃头', '整手足甲', '求医疗病', '裁制',
              '营建', '修宫室', '缮城郭', '筑堤防', '修造', '竖柱上梁', '修仓库', '鼓铸', '经络', '酝酿', '开市', '立券交易', '纳财', '开仓', '修置产室', '开渠',
              '穿井', '安碓硙', '塞穴', '补垣', '修饰垣墙', '平治道涂', '破屋坏垣', '伐木', '栽种', '牧养', '纳畜', '破土', '安葬', '启攒']),
            ('月忌', ldn, (5, 14, 23), [], ['出行', '乘船渡水']),
            ('月虚', '未辰丑戌未辰丑戌未辰丑戌'[men], d, [], ['修仓库', '纳财', '开仓']),
            ('灾煞', '午卯子酉午卯子酉午卯子酉'[men], d, [],
             ['祈福', '求嗣', '上册', '上表章', '颁诏', '施恩', '招贤', '举正直', '宣政事', '布政事', '庆赐', '宴会', '冠带', '出行', '安抚边境', '选将',
              '出师', '上官', '临政', '结婚姻', '纳采', '嫁娶', '进人口', '搬移', '安床', '解除', '整容', '剃头', '整手足甲', '求医疗病', '裁制', '营建',
              '修宫室', '缮城郭', '筑堤防', '修造', '竖柱上梁', '修仓库', '鼓铸', '经络', '酝酿', '开市', '立券交易', '纳财', '开仓', '修置产室', '开渠', '穿井',
              '安碓硙', '塞穴', '补垣', '修饰垣墙', '破屋坏垣', '栽种', '牧养', '纳畜', '破土', '安葬', '启攒']),
            ('劫煞', '巳寅亥申巳寅亥申巳寅亥申'[men], d, [],
             ['祈福', '求嗣', '上册', '上表章', '颁诏', '施恩', '招贤', '举正直', '宣政事', '布政事', '庆赐', '宴会', '冠带', '出行', '安抚边境', '选将',
              '出师', '上官', '临政', '结婚姻', '纳采', '嫁娶', '进人口', '搬移', '安床', '解除', '整容', '剃头', '整手足甲', '求医疗病', '裁制', '营建',
              '修宫室', '缮城郭', '筑堤防', '修造', '竖柱上梁', '修仓库', '鼓铸', '经络', '酝酿', '开市', '立券交易', '纳财', '开仓', '修置产室', '开渠', '穿井',
              '安碓硙', '塞穴', '补垣', '修饰垣墙', '破屋坏垣', '栽种', '牧养', '纳畜', '破土', '安葬', '启攒']),
            ('厌对', '午巳辰卯寅丑子亥戌酉申未'[men], d, [], ['嫁娶']),  # 六仪招摇
            ('招摇', '午巳辰卯寅丑子亥戌酉申未'[men], d, [], ['取鱼', '乘船渡水']),  # 六仪厌对
            ('小红砂', '酉丑巳酉丑巳酉丑巳酉丑巳'[men], d, [], ['嫁娶']),
            # ('人隔', '丑亥酉未巳卯丑亥酉未巳卯'[men], d, ['嫁娶', '进人']),
            ('往亡', '戌丑寅巳申亥卯午酉子辰未'[men], d, [],
             ['上册', '上表章', '颁诏', '招贤', '宣政事', '出行', '安抚边境', '选将', '出师', '上官', '临政', '嫁娶', '进人口', '搬移', '求医疗病', '捕捉',
              '畋猎', '取鱼']),
            ('重丧', '癸己甲乙己丙丁己庚辛己壬'[men], d, [], ['嫁娶', '安葬']),
            ('重复', '癸己庚辛己壬癸戊甲乙己壬'[men], d, [], ['嫁娶', '安葬']),
            ('杨公忌', (lmn, ldn), mrY13, [], ['开张', '修造', '嫁娶', '立券']),  # 杨筠松根据“二十八星宿”顺数，订定了“杨公十三忌”
            ('神号', '申酉戌亥子丑寅卯辰巳午未'[men], d, [], []),
            ('妨择', '辰辰午午申申戌戌子子寅寅'[men], d, [], []),
            ('披麻', '午卯子酉午卯子酉午卯子酉'[men], d, [], ['嫁娶', '入宅']),
            # ('冰消瓦陷', '酉辰巳子丑申卯戌亥午未寅'[men], d, [], ['修造']),
            ('大耗', '辰巳午未申酉戌亥子丑寅卯'[men], d, [], ['修仓库', '开市', '立券交易', '纳财', '开仓']),  # 历例曰：“大耗者，岁中虚耗之神也。所理之地不可营造仓库、纳财物
            ('伏兵', '丙甲壬庚'[yen % 4], d[0], [], ['修仓库', '修造', '出师']),
            ('大祸', '丁乙癸辛'[yen % 4], d[0], [], ['修仓库', '修造', '出师']),
            ('天吏', '卯子酉午卯子酉午卯子酉午'[men], d, [],
             ['祈福', '求嗣', '上册', '上表章', '施恩', '招贤', '举正直', '冠带', '出行', '安抚边境', '选将', '出师', '上官', '临政', '结婚姻', '纳采', '嫁娶',
              '进人口', '搬移', '安床', '解除', '求医疗病', '营建', '修宫室', '缮城郭', '筑堤防', '修造', '竖柱上梁', '修仓库', '开市', '立券交易', '纳财', '开仓',
              '修置产室', '栽种', '牧养', '纳畜']),
            ('天瘟', '丑卯未戌辰寅午子酉申巳亥'[men], d, [], ['修造', '求医疗病', '纳畜']),  # 参考修正
            ('天狱', '午酉子卯午酉子卯午酉子卯'[men], d, [], []),
            ('天火', '午酉子卯午酉子卯午酉子卯'[men], d, [], ['苫盖']),
            ('天棒', '寅辰午申戌子寅辰午申戌子'[men], d, [], []),
            ('天狗', '寅卯辰巳午未申酉戌亥子丑'[men], d, [], ['祭祀']),
            ('天狗下食', '戌亥子丑寅卯辰巳午未申酉'[men], d, [], ['祭祀']),
            ('天贼', '卯寅丑子亥戌酉申未午巳辰'[men], d, [], ['出行', '修仓库', '开仓']),
            ('地囊', d,
             ['辛未辛酉', '乙酉乙未', '庚子庚午', '癸未癸丑', '甲子甲寅', '己卯己丑', '戊辰戊午', '癸未癸巳', '丙寅丙申', '丁卯丁巳', '戊辰戊子', '庚戌庚子', ][men],
             [], ['营建', '修宫室', '缮城郭', '筑堤防', '修造', '修仓库', '修置产室', '开渠', '穿井', '安碓硙', '补垣', '修饰垣墙', '平治道涂', '破屋坏垣', '栽种',
                  '破土']),
            ('地火', '子亥戌酉申未午巳辰卯寅丑'[men], d, [], ['栽种']),
            ('独火', '未午巳辰卯寅丑子亥戌酉申'[men], d, [], ['修造']),
            ('受死', '卯酉戌辰亥巳子午丑未寅申'[men], d, [], ['畋猎']),
            ('黄沙', '寅子午寅子午寅子午寅子午'[men], d, [], ['出行']),
            ('六不成', '卯未寅午戌巳酉丑申子辰亥'[men], d, [], ['修造']),
            ('小耗', '卯辰巳午未申酉戌亥子丑寅'[men], d, [], ['修仓库', '开市', '立券交易', '纳财', '开仓']),
            ('神隔', '酉未巳卯丑亥酉未巳卯丑亥'[men], d, [], ['祭祀', '祈福']),
            ('朱雀', '亥丑卯巳未酉亥丑卯巳未酉'[men], d, [], ['嫁娶']),
            ('白虎', '寅辰午申戌子寅辰午申戌子'[men], d, [], ['安葬']),
            ('玄武', '巳未酉亥丑卯巳未酉亥丑卯'[men], d, [], ['安葬']),
            ('勾陈', '未酉亥丑卯巳未酉亥丑卯巳'[men], d, [], []),
            ('木马', '辰午巳未酉申戌子亥丑卯寅'[men], d, [], []),
            ('破败', '辰午申戌子寅辰午申戌子寅'[men], d, [], []),
            ('殃败', '巳辰卯寅丑子亥戌酉申未午'[men], d, [], []),
            ('雷公', '巳申寅亥巳申寅亥巳申寅亥'[men], d, [], []),
            ('飞廉', '申酉戌巳午未寅卯辰亥子丑'[men], d, [], ['纳畜', '修造', '搬移', '嫁娶']),
            ('大煞', '申酉戌巳午未寅卯辰亥子丑'[men], d, [], ['安抚边境', '选将', '出师']),
            # 《神枢经》曰：“飞廉者，岁之廉察使君之象，亦名大煞。所理之不可兴工、动土，搬移，嫁娶《广圣历》曰：“子年在申，丑年在酉，寅年在戌，卯年在巳，辰年在午，巳年在未，午年在寅，未年在卯，申 年在辰，酉年在亥，戌年在子，亥年在丑也。”
            ('枯鱼', '申巳辰丑戌未卯子酉午寅亥'[men], d, [], ['栽种']),
            ('九空', '申巳辰丑戌未卯子酉午寅亥'[men], d, [], ['进人口', '修仓库', '开市', '立券交易', '纳财', '开仓']),
            ('八座', '酉戌亥子丑寅卯辰巳午未申'[men], d, [], []),
            ('八风触水龙', d, ('丁丑己酉', '甲申甲辰', '辛未丁未', '甲戌甲寅')[sn], [], ['取鱼', '乘船渡水']),
            ('血忌', '午子丑未寅申卯酉辰戌巳亥'[men], d, [], ['针刺']),
            ('阴错', '壬子癸丑庚寅辛卯庚辰丁巳丙午丁未甲申乙酉甲戌癸亥'[men * 2:men * 2 + 2], d, [], []),
            ('三娘煞', ldn, (3, 7, 13, 18, 22, 27), [], ['嫁娶']),
            ('四绝', tmd, t4j, [], ['出行', '上官', '嫁娶', '进人口', '搬移', '开市', '立券交易', '祭祀']),
            ('四离', tmd, t4l, [], ['出行', '嫁娶']),
            ('四击', '未未戌戌戌丑丑丑辰辰辰未'[men], d, [], ['安抚边境', '选将', '出师']),
            # 四击者,春戌、夏丑、秋辰、冬未。按四击者,四时所冲之墓辰也。如正二三月建寅卯辰,辰与戌冲,故戌为四击也。馀仿此。
            # ('四正废', d, '庚申辛酉壬子癸亥甲寅乙卯丙午丁巳'[sn * 4:sn * 4 + 4], ['修造', '交易', '安床']),
            ('四耗', d, ('壬子', '乙卯', '戊午', '辛酉')[sn], [], ['安抚边境', '选将', '出师', '修仓库', '开市', '立券交易', '纳财', '开仓']),
            ('四穷', d, ('乙亥', '丁亥', '辛亥', '癸亥')[sn], [],
             ['安抚边境', '选将', '出师', '结婚姻', '纳采', '嫁娶', '进人口', '修仓库', '开市', '立券交易', '纳财', '开仓', '安葬']),
            ('四忌', d, ('甲子', '丙子', '庚子', '壬子')[sn], [], ['安抚边境', '选将', '出师', '结婚姻', '纳采', '嫁娶', '安葬']),
            ('四废', d, ('庚申辛酉', '壬子癸亥', '甲寅乙卯', '丁巳丙午')[sn], [],
             ['祈福', '求嗣', '上册', '上表章', '颁诏', '施恩', '招贤', '举正直', '宣政事', '布政事', '庆赐', '宴会', '冠带', '出行', '安抚边境', '选将',
              '出师', '上官', '临政', '结婚姻', '纳采', '嫁娶', '进人口', '搬移', '安床', '解除', '求医疗病', '裁制', '营建', '修宫室', '缮城郭', '筑堤防',
              '修造', '竖柱上梁', '修仓库', '鼓铸', '经络', '酝酿', '开市', '立券交易', '纳财', '开仓', '修置产室', '开渠', '穿井', '安碓硙', '塞穴', '补垣',
              '修饰垣墙', '栽种', '牧养', '纳畜', '破土', '安葬', '启攒']),  # 庚申辛酉为春废，壬子癸亥夏时当。甲寅乙卯秋月值，丁巳丙午冬季防。
            ('五墓', ['壬辰', '戊辰', '乙未', '乙未', '戊辰', '丙戌', '丙戌', '戊辰', '辛丑', '辛丑', '戊辰', '壬辰'][men], d, [],
             ['冠带', '出行', '安抚边境', '选将', '出师', '上官', '临政', '结婚姻', '纳采', '嫁娶', '进人口', '搬移', '安床', '解除', '求医疗病', '营建',
              '修宫室', '缮城郭', '筑堤防', '修造', '竖柱上梁', '开市', '立券交易', '修置产室', '栽种', '牧养', '纳畜', '破土', '安葬', '启攒']),
            ('五虚', d[1], ['巳酉丑', '申子辰', '亥卯未', '寅午戌'][sn], [], ['修仓库', '开仓']),
            ('五离', d[1], '申酉', ['沐浴'], ['庆赐', '宴会', '结婚姻', '纳采', '立券交易']),  # 除神
            ('五鬼', '未戌午寅辰酉卯申丑巳子亥'[men], d, [], ['出行']),
            ('八专', d, ['丁未', '己未', '庚申', '甲寅', '癸丑'], [], ['安抚边境', '选将', '出师', '结婚姻', '纳采', '嫁娶']),
            ('九坎', '申巳辰丑戌未卯子酉午寅亥'[men], d, [], ['塞穴', '补垣', '取鱼', '乘船渡水']),
            # 《广圣历》曰:九坎者,月中杀神也。其日忌乘船渡水、修堤防、筑垣墙、苫盖屋舍。《历例》曰:九坎者,正月在辰逆行四季,五月在卯逆行四仲,九月在寅逆行四孟。
            ('九焦', '申巳辰丑戌未卯子酉午寅亥'[men], d, [], ['鼓铸', '栽种']),
            # 天转有四日，分别是春季的乙卯日，夏季的丙午日，秋季的辛酉日，冬季的壬子日。
            # 地转也有四日，分别是春季的辛卯日，夏季的戊午日，秋季的癸酉日，冬季的丙子日。
            # “春季乙辛到兔位，夏天丙戊马上求；秋来辛癸听鸡叫，冬寒丙壬鼠洞留”。
            ('天转', '乙卯丙午辛酉壬子'[sn * 2:sn * 2 + 2], d, [], ['修造', '搬移', '嫁娶']),
            ('地转', '辛卯戊午癸酉丙子'[sn * 2:sn * 2 + 2], d, [], ['修造', '搬移', '嫁娶']),
            ('月建转杀', '卯午酉子'[sn], d, [], ['修造']),
            ('荒芜', d[1], '巳酉丑申子辰亥卯未寅午戌'[sn * 3:sn * 3 + 3], [], []),

            ('蚩尤', '戌子寅辰午申'[men % 6], d, [], []),  # 正七逢寅二八辰，三九午上四十申。五十一月原在戌，六十二月子为真。
            ('大时', '酉午卯子酉午卯子酉午卯子'[men], d, [],
             ['祈福', '求嗣', '上册', '上表章', '施恩', '招贤', '举正直', '冠带', '出行', '安抚边境', '选将', '出师', '上官', '临政', '结婚姻', '纳采', '嫁娶',
              '进人口', '搬移', '安床', '解除', '求医疗病', '营建', '修宫室', '缮城郭', '筑堤防', '修造', '竖柱上梁', '修仓库', '开市', '立券交易', '纳财', '开仓',
              '修置产室', '栽种', '牧养', '纳畜']),
            # 《神枢经》曰:大时者,将军之象也。所直之日,忌出军攻战、筑室会亲。李鼎祚曰:大时者,正月起卯逆行四仲。
            ('大败', '酉午卯子酉午卯子酉午卯子'[men], d, [], []),
            # 十恶大败干支纪日分别为：甲辰、乙巳、丙申、丁亥、戊戌、己丑、庚辰、辛巳、壬申、癸亥。（不确定）《总要历》曰:大败者,兵败忌辰也。其日忌临阵侵敌、攻城野战。《历例》曰:正月起卯,逆行四仲。

            # 《枢要历》曰:五虛者,四时绝辰也。其日忌开仓、营种莳、出财宝、放债负。《历例》曰:五虚者,春巳酉丑,夏申子辰,秋亥卯未,冬寅午戌也。
            ('咸池', '酉午卯子酉午卯子酉午卯子'[men], d, [], ['嫁娶', '取鱼', '乘船渡水']),  # 《历例》曰:咸池者,正月起卯,逆行四仲;
            # 《历例》曰:士符者,正月丑，二月已,三月酉,四月寅,五月午,六月戌,七月卯,八月未,九月亥,十月辰,十一月申,十二月子。
            ('土符', '申子丑巳酉寅午戌卯未亥辰'[men], d, [],
             ['营建', '修宫室', '缮城郭', '筑堤防', '修造', '修仓库', '修置产室', '开渠', '穿井', '安碓硙', '补垣', '修饰垣墙', '平治道涂', '破屋坏垣', '栽种',
              '破土']),
            ('土府', '子丑寅卯辰巳午未申酉戌亥'[men], d, [],
             ['营建', '修宫室', '缮城郭', '筑堤防', '修造', '修仓库', '修置产室', '开渠', '穿井', '安碓硙', '补垣', '修饰垣墙', '平治道涂', '破屋坏垣', '栽种',
              '破土']),
            ('土王用事', (datetime(self.nextSolarTermYear, twys[0], twys[1]) - self.date).days, range(0, 18), [],
             ['营建', '修宫室', '缮城郭', '筑堤防', '修造', '修仓库', '修置产室', '开渠', '穿井', '安碓硙', '补垣', '修饰垣墙', '平治道涂', '破屋坏垣', '栽种',
              '破土']),
            ('血支', '亥子丑寅卯辰巳午未申酉戌'[men], d, [], ['针刺']),
            # 《广圣历》曰:九焦者,月中杀神也。其日忌炉冶、铸造、种植、修筑园圃。《历例》曰:正月在辰逆行四季,五月在卯逆行四仲,九月在寅逆行四孟。
            ('游祸', '亥申巳寅亥申巳寅亥申巳寅'[men], d, [], ['祈福', '求嗣', '解除', '求医疗病']),
            # 官历宜服药?  《神枢经》曰:游祸者,月中恶神也。其日忌服药请医、祀神致祭。李鼎祚曰:游祸者,正月起已逆行四孟。
            ('归忌', '寅子丑寅子丑寅子丑寅子丑'[men], d, [], ['搬移', '远回']),
            # 《广圣历》:归忌者,月内凶神也。其日忌远行、归家移徙、娶归、《历例》曰:孟月丑,仲月寅,季月子
            ('岁薄', (lmn, d), [(4, '戊午'), (4, '丙午'), (10, '壬子'), (10, '戊子')], [], []),
            ('逐阵', (lmn, d), [(6, '戊午'), (6, '丙午'), (12, '壬子'), (12, '戊子')], [], []),
            ('阴阳交破', (lmn, d), [(10, '丁巳')], [], []),
            ('宝日', d, ['丁未', '丁丑', '丙戌', '甲午', '庚子', '壬寅', '癸卯', '乙巳', '戊申', '己酉', '辛亥', '丙辰'], [], []),
            ('义日', d, ['甲子', '丙寅', '丁卯', '己巳', '辛未', '壬申', '癸酉', '乙亥', '庚辰', '辛丑', '庚戌', '戊午'], [], []),
            ('制日', d, ['乙丑', '甲戌', '壬午', '戊子', '庚寅', '辛卯', '癸巳', '乙未', '丙申', '丁酉', '己亥', '甲辰'], [], []),
            ('伐日', d, ['庚午', '辛巳', '丙子', '戊寅', '己卯', '癸未', '癸丑', '甲申', '乙酉', '丁亥', '壬辰', '壬戌'], [],
             ['安抚边境', '选将', '出师']),
            ('专日', d, ['甲寅', '乙卯', '丁巳', '丙午', '庚申', '辛酉', '癸亥', '壬子', '戊辰', '戊戌', '己丑', '己未'], [],
             ['安抚边境', '选将', '出师']),
            ('重日', d[1], '巳亥', [], ['破土', '安葬', '启攒']),
            ('复日', '癸巳甲乙戊丙丁巳庚辛戊壬'[men], d, ['裁制'], ['破土', '安葬', '启攒']),
            # 《天宝历》曰:复日者,为魁罡所系之辰也。其日忌为凶事,利为吉事。《历例》曰:复日者,正、七月甲庚,二、八月乙辛,四十月丙壬,五、十一月丁癸,三、九、六、十二月戊巳日也。
        ]

        # 配合angel、demon的数据结构的吉神凶神筛选
        def getTodayGoodBadThing(dic):
            for i in [(angel, 'goodName', 'goodThing', 'badThing'), (demon, 'badName', 'goodThing', 'badThing')]:
                godDb, godNameKey, goodThingKey, badThingKey = i[0], i[1], i[2], i[3]
                for godItem in godDb:
                    # print(x, x[1] , x[2]) 输出当日判断结果x[1]，看x[1]是否落在判断范围x[2]里面
                    if godItem[1] in godItem[2]:
                        dic[godNameKey] += [godItem[0]]
                        dic[goodThingKey] += godItem[3]
                        dic[badThingKey] += godItem[4]
                # 宜列、忌列分别去重
                dic[goodThingKey] = list(set(dic[goodThingKey]))
                dic[badThingKey] = list(set(dic[badThingKey]))
            return dic

        gbDic = getTodayGoodBadThing(gbDic)
        self.goodGodName = gbDic['goodName']
        self.badGodName = gbDic['badName']

        # 第一方案：《钦定协纪辨方书》古书影印版，宜忌等第表
        # 凡铺注《万年历》、《通书》，先依用事次第察其所宜忌之日，于某日下注宜某事，某日下注忌某事，次按宜忌，较量其凶吉之轻重，以定去取。
        # 从忌亦从宜
        def badDrewGood(dic):
            for removeThing in list(set(dic['goodThing']).intersection(set(dic['badThing']))):
                dic['goodThing'].remove(removeThing)
                dic['badThing'].remove(removeThing)
            return dic

        # 从忌不从宜
        def badOppressGood(dic):
            for removeThing in list(set(dic['goodThing']).intersection(set(dic['badThing']))):
                dic['goodThing'].remove(removeThing)
            return dic

        # 从宜不从忌
        def goodOppressBad(dic):
            for removeThing in list(set(dic['goodThing']).intersection(set(dic['badThing']))):
                dic['badThing'].remove(removeThing)
            return dic

        # 诸事不宜
        def nothingGood(dic):
            dic['goodThing'] = ['诸事不宜']
            dic['badThing'] = ['诸事不宜']
            return dic

        # 今日凶吉判断
        thingLevel = self.getTodayThingLevel()

        # 0:'从宜不从忌',1:'从宜亦从忌',2:'从忌不从宜',3:'诸事皆忌'
        if thingLevel == 3:
            gbDic = nothingGood(gbDic)
        elif thingLevel == 2:
            gbDic = badOppressGood(gbDic)
        elif thingLevel == 1:
            gbDic = badDrewGood(gbDic)
        else:
            gbDic = goodOppressBad(gbDic)

        self.goodThing = gbDic['goodThing']
        self.badThing = gbDic['badThing']

        # 遇德犹忌之事
        deIsBadThingDic = {}
        for i in angel[:6]:
            deIsBadThingDic[i[0]] = i[4]
        deIsBadThing = []
        if self.isDe:
            for i in self.goodGodName:
                if i in deIsBadThingDic:
                    deIsBadThing += deIsBadThingDic[i]
        deIsBadThing = list(set(deIsBadThing))
        if thingLevel != 3:
            # 凡宜宣政事，布政事之日，只注宜宣政事。
            if '宣政事' in self.goodThing and '布政事' in self.goodThing:
                self.goodThing.remove('布政事')
            # 凡宜营建宫室、修宫室之日，只注宜营建宫室。
            if '营建宫室' in self.goodThing and '修宫室' in self.goodThing:
                self.goodThing.remove('修宫室')
            # 凡德合、赦愿、月恩、四相、时德等日，不注忌进人口、安床、经络、酝酿、开市、立券、交易、纳财、开仓库、出货财。如遇德犹忌，及从忌不从宜之日，则仍注忌。
            temp = False
            for i in self.goodGodName:
                if i in ['岁德合', '月德合', '天德合', '天赦', '天愿', '月恩', '四相', '时德']:
                    temp = True
                    break
            if temp:
                # 如遇德犹忌，及从忌不从宜之日，则仍注忌。
                if i not in deIsBadThing or thingLevel != 2:
                    self.badThing = rfRemove(self.badThing, ['进人口', '安床', '经络', '酝酿', '开市', '立券交易', '纳财', '开仓库', '出货财'])

            # 凡天狗寅日忌祭祀，不注宜求福、祈嗣。
            if '天狗' in self.goodGodName or '寅' in d:
                self.badThing = rfAdd(self.badThing, addList=['祭祀'])
                self.goodThing = rfRemove(self.goodThing, removeList=['祭祀'])

                self.goodThing = rfRemove(self.goodThing, removeList=['求福', '祈嗣'])
            # 凡卯日忌穿井，不注宜开渠。壬日忌开渠，不注宜穿井。
            if '卯' in d:
                self.badThing = rfAdd(self.badThing, addList=['穿井'])
                self.goodThing = rfRemove(self.goodThing, removeList=['穿井'])

                self.goodThing = rfRemove(self.goodThing, removeList=['开渠'])
            if '壬' in d:
                self.badThing = rfAdd(self.badThing, addList=['开渠'])
                self.goodThing = rfRemove(self.goodThing, removeList=['开渠'])

                self.goodThing = rfRemove(self.goodThing, removeList=['穿井'])
            # 凡巳日忌出行，不注宜出师、遣使。
            if '巳' in d:
                self.badThing = rfAdd(self.badThing, addList=['出行'])
                self.goodThing = rfRemove(self.goodThing, removeList=['出行'])

                self.goodThing = rfRemove(self.goodThing, removeList=['出师', '遣使'])
            # 凡酉日忌宴会，亦不注宜庆赐、赏贺。
            if '酉' in d:
                self.badThing = rfAdd(self.badThing, addList=['宴会'])
                self.goodThing = rfRemove(self.goodThing, removeList=['宴会'])

                self.goodThing = rfRemove(self.goodThing, removeList=['庆赐', '赏贺'])
            # 凡丁日忌剃头，亦不注宜整容。
            if '丁' in d:
                self.badThing = rfAdd(self.badThing, addList=['剃头'])
                self.goodThing = rfRemove(self.goodThing, removeList=['剃头'])

                self.goodThing = rfRemove(self.goodThing, removeList=['整容'])
            # 凡吉足胜凶，从宜不从忌者，如遇德犹忌之事，则仍注忌。
            if self.todayLevel == 0 and thingLevel == 0:
                self.badThing = rfAdd(self.badThing, addList=deIsBadThing)
            # 凡吉凶相抵，不注宜亦不注忌者，如遇德犹忌之事，则仍注忌。
            if self.todayLevel == 1:
                self.badThing = rfAdd(self.badThing, addList=deIsBadThing)
                # 凡吉凶相抵，不注忌祈福，亦不注忌求嗣。
                if '祈福' not in self.badThing:
                    self.badThing = rfRemove(self.badThing, removeList=['求嗣'])
                # 凡吉凶相抵，不注忌结婚姻，亦不注忌冠带、纳采问名、嫁娶、进人口，如遇德犹忌之日则仍注忌。
                if '结婚姻' not in self.badThing and not self.isDe:
                    self.badThing = rfRemove(self.badThing, removeList=['冠带', '纳采问名', '嫁娶', '进人口'])
                # 凡吉凶相抵，不注忌嫁娶，亦不注忌冠带、结婚姻、纳采问名、进人口、搬移、安床，如遇德犹忌之日，则仍注忌。
                if '嫁娶' not in self.badThing and not self.isDe:
                    # 遇不将而不注忌嫁娶者，亦仍注忌。
                    if '不将' in self.goodGodName:
                        pass
                    else:
                        self.badThing = rfRemove(self.badThing, removeList=['冠带', '纳采问名', '结婚姻', '进人口', '搬移', '安床'])
            # 遇亥日、厌对、八专、四忌、四穷而仍注忌嫁娶者，只注所忌之事，其不忌者仍不注忌。【未妥善解决】
            if '亥' in d:
                self.badThing = rfAdd(self.badThing, ['嫁娶'])
            # 凡吉凶相抵，不注忌搬移，亦不注忌安床。不注忌安床，亦不注忌搬移。如遇德犹忌之日，则仍注忌。
            if self.todayLevel == 1 and not self.isDe:
                if '搬移' not in self.badThing:
                    self.badThing = rfRemove(self.badThing, removeList=['安床'])
                if '安床' not in self.badThing:
                    self.badThing = rfRemove(self.badThing, removeList=['搬移'])
                # 凡吉凶相抵，不注忌解除，亦不注忌整容、剃头、整手足甲。如遇德犹忌之日，则仍注忌。
                if '解除' not in self.badThing:
                    self.badThing = rfRemove(self.badThing, removeList=['整容', '剃头', '整手足甲'])
                # 凡吉凶相抵，不注忌修造动土、竖柱上梁，亦不注忌修宫室、缮城郭、筑提防、修仓库、鼓铸、苫盖、修置产室、开渠穿井、安碓硙、补垣塞穴、修饰垣墙、平治道涂、破屋坏垣。如遇德犹忌之日，则仍注忌。
                if '修造' not in self.badThing or '竖柱上梁' not in self.badThing:
                    self.badThing = rfRemove(self.badThing,
                                             removeList=['修宫室', '缮城郭', '整手足甲', '筑提', '修仓库', '鼓铸', '苫盖', '修置产室', '开渠穿井',
                                                         '安碓硙', '补垣塞穴', '修饰垣墙', '平治道涂', '破屋坏垣'])
            # 凡吉凶相抵，不注忌开市，亦不注忌立券交易、纳财。不注忌纳财，亦不注忌开市、立券交易。不注忌立券交易，亦不注忌开市、纳财。
            # 凡吉凶相抵，不注忌开市、立券交易，亦不注忌开仓库、出货财。
            if self.todayLevel == 1:
                if '开市' not in self.badThing:
                    self.badThing = rfRemove(self.badThing, removeList=['立券交易', '纳财', '开仓库', '出货财'])
                if '纳财' not in self.badThing:
                    self.badThing = rfRemove(self.badThing, removeList=['立券交易', '开市'])
                if '立券交易' not in self.badThing:
                    self.badThing = rfRemove(self.badThing, removeList=['纳财', '开市', '开仓库', '出货财'])

            # 如遇专忌之日，则仍注忌。【未妥善解决】
            # 凡吉凶相抵，不注忌牧养，亦不注忌纳畜。不注忌纳畜，亦不注忌牧养。
            if self.todayLevel == 1:
                if '牧养' not in self.badThing:
                    self.badThing = rfRemove(self.badThing, removeList=['纳畜'])
                if '纳畜' not in self.badThing:
                    self.badThing = rfRemove(self.badThing, removeList=['牧养'])
                # 凡吉凶相抵，有宜安葬不注忌启攒，有宜启攒不注忌安葬。
                if '安葬' in self.goodThing:
                    self.badThing = rfRemove(self.badThing, removeList=['启攒'])
                if '启攒' in self.goodThing:
                    self.badThing = rfRemove(self.badThing, removeList=['安葬'])
            # 凡忌诏命公卿、招贤，不注宜施恩、封拜、举正直、袭爵受封。    #本版本无 封拜 袭爵受封
            if '诏命公卿' in self.badThing or '招贤' in self.badThing:
                self.goodThing = rfRemove(self.goodThing, removeList=['施恩', '举正直'])
            # 凡忌施恩、封拜、举正直、袭爵受封，亦不注宜诏命公卿、招贤。
            if '施恩' in self.badThing or '举正直' in self.badThing:
                self.goodThing = rfRemove(self.goodThing, removeList=['诏命公卿', '招贤'])
            # 凡宜宣政事之日遇往亡则改宣为布。
            if '宣政事' in self.goodThing and '往亡' in self.badGodName:
                self.goodThing.remove('宣政事')
                self.goodThing = rfAdd(self.goodThing, addList=['布政事'])
            # 凡月厌忌行幸、上官，不注宜颁诏、施恩封拜、诏命公卿、招贤、举正直。遇宜宣政事之日，则改宣为布。
            if '月厌' in self.badGodName:
                self.goodThing = rfRemove(self.goodThing, removeList=['颁诏', '施恩', '招贤', '举正直', '宣政事'])
                self.goodThing = rfAdd(self.goodThing, addList=['布政事'])
                # 凡土府、土符、地囊，只注忌补垣，亦不注宜塞穴。
                self.badThing = rfAdd(self.badThing, addList=['补垣'])
                if '土府' in self.badGodName or '土符' in self.badGodName or '地囊' in self.badGodName:
                    self.goodThing = rfRemove(self.goodThing, removeList=['塞穴'])
            # 凡开日，不注宜破土、安葬、启攒，亦不注忌。遇忌则注。
            if '开' in self.today12DayOfficer:
                self.goodThing = rfRemove(self.goodThing, removeList=['破土', '安葬', '启攒'])
            # 凡四忌、四穷只忌安葬。如遇鸣吠、鸣吠对亦不注宜破土、启攒。
            if '四忌' in self.badGodName or '四忌' in self.badGodName:
                self.badThing = rfAdd(self.badThing, addList=['安葬'])
                self.goodThing = rfRemove(self.goodThing, removeList=['破土', '启攒'])
            if '鸣吠' in self.badGodName or '鸣吠对' in self.badGodName:
                self.goodThing = rfRemove(self.goodThing, removeList=['破土', '启攒'])
            # 凡天吏、大时不以死败论者，遇四废、岁薄、逐阵仍以死败论。
            # 凡岁薄、逐阵日所宜事，照月厌所忌删，所忌仍从本日。、
            # 二月甲戌、四月丙申、六月甲子、七月戊申、八月庚辰、九月辛卯、十月甲子、十二月甲子，德和与赦、愿所汇之辰，诸事不忌。
            if ['空', '甲戌', '空', '丙申', '空', '甲子', '戊申', '庚辰', '辛卯', '甲子', '空', '甲子'][lmn - 1] in d:
                self.badThing = ['诸事不忌']
            if len(set(self.goodGodName).intersection(set(['岁德合', '月德合', '天德合']))) and len(
                    set(self.goodGodName).intersection(set(['天赦', '天愿']))):
                self.badThing = ['诸事不忌']

            # 书中未明注忌不注宜
        rmThing = []
        for thing in self.badThing:
            if thing in self.goodThing:
                rmThing.append(thing)
        if len(rmThing) == 1 and '诸事' in rmThing[0]:
            pass
        else:
            self.goodThing = rfRemove(self.goodThing, removeList=rmThing)

        # 为空清理
        if self.badThing == []:
            self.badThing = ['诸事不忌']
        if self.goodThing == []:
            self.goodThing = ['诸事不宜']

        # 输出排序调整
        self.badThing.sort(key=sortCollation)
        self.goodThing.sort(key=sortCollation)
        return (self.goodGodName, self.badGodName), (self.goodThing, self.badThing)
