# pyGregorian2LunarCalendar
# coding=UTF-8
# 1901~2100年农历数据表
# author: cuba3, github: https://github.com/cuba3/pyGregorian2LunarCalendar
# base code by Yovey , https://www.jianshu.com/p/8dc0d7ba2c2a
# powered by Late Lee, http://www.latelee.org/python/python-yangli-to-nongli.html#comment-78
# other author:Chen Jian, http://www.cnblogs.com/chjbbs/p/5704326.html
# 数据来源: http://data.weather.gov.hk/gts/time/conversion1_text_c.htm


from datetime import datetime, timedelta
from config import *
from holidays import otherLunarHolidaysList, otherHolidaysList, legalsolarTermsHolidayDic, legalHolidaysDic, \
    legalLunarHolidaysDic
from solar24 import getTheYearAllSolarTermsList

class Lunar():
    def __init__(self,date):
        self.date = date
        self.twohourNum = (self.date.hour + 1) // 2
        self._upper_year = ''
        (self.lunarYear, self.lunarMonth, self.lunarDay) = self.get_lunarDateNum()
        (self.lunarYearCn,self.lunarMonthCn,self.lunarDayCn)=self.get_lunarCn()

        (self.year8Char, self.month8Char, self.day8Char) = self.get_the8char()
        self.get_earthNum(),self.get_heavenNum(),self.get_season()
        self.twohour8CharList = self.get_twohour8CharList()
        self.twohour8Char = self.get_twohour8Char()
        self.get_today12DayOfficer()

        self.chineseYearZodiac=self.get_chineseYearZodiac()
        self.chineseZodiacClash=self.get_chineseZodiacClash()
        self.weekDayCn=self.get_weekDayCn()
        self.todaySolarTerms=self.get_todaySolarTerms()
        self.thisYearSolarTermsDic=dict(zip(solarTermsNameList, self.solarTermsDateList))

        self.today28Star=self.get_the28Stars()
    def get_lunarYearCN(self):
        for i in str(self.lunarYear):
            self._upper_year += upperNum[int(i)]
        return self._upper_year
    def get_lunarMonthCN(self):
        leap = (self.lunarMonth >> 4) & 0xf
        m = self.lunarMonth & 0xf
        lunarMonth = lunarMonthNameList[(m - 1) % 12]
        thisLunarMonthDays=self.monthDaysList[0]
        if leap == m:
            lunarMonth = "闰" + lunarMonth
            thisLunarMonthDays = self.monthDaysList[2]
        if thisLunarMonthDays < 30:
            return lunarMonth+'小'
        else:
            return lunarMonth + '大'
    def get_lunarCn(self):
        return self.get_lunarYearCN(), self.get_lunarMonthCN(), lunarDayNameList[(self.lunarDay - 1) % 30]
    # 生肖
    def get_chineseYearZodiac(self):
        return chineseZodiacNameList[(self.lunarYear - 4) % 12]
    def get_chineseZodiacClash(self):
        zodiacNum=self.dayEarthNum
        zodiacClashNum=(zodiacNum+ 6) % 12
        self.zodiacMark6=chineseZodiacNameList[(25-zodiacNum)%12]
        self.zodiacMark3List=[chineseZodiacNameList[(zodiacNum+4)%12],chineseZodiacNameList[(zodiacNum+8)%12]]
        self.zodiacWin=chineseZodiacNameList[zodiacNum]
        self.zodiacLose=chineseZodiacNameList[zodiacClashNum]
        return self.zodiacWin+'日冲'+self.zodiacLose

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
        leap_month, leap_day, month_day = 0, 0, 0  # 闰几月，该月多少天 传入月份多少天
        tmp = lunarMonthData[self.lunarYear - START_YEAR] # 获取16进制数据12-1月份农历日数 0=29天 1=30天
        # 表示获取当前月份的布尔值:指定二进制1（假定真），向左移动月数-1，与当年全年月度数据合并取出2进制位作为判断
        if tmp & (1 << (self.lunarMonth - 1)):
            month_day = 30
        else:
            month_day = 29
        # 闰月
        leap_month = (tmp >> month_NUM_BIT) & 0xf
        if leap_month:
            if (tmp & (1 << month_DAY_BIT)):
                leap_day = 30
            else:
                leap_day = 29
        self.monthDaysList=[month_day, leap_month, leap_day]
        return month_day, leap_month, leap_day
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
            _month_days, _leap_month, _leap_day = self.getMonthLeapMonthLeapDays()
            while _span_days >= _month_days:
                """ 获取当前月份天数，从差日中扣除 """
                _span_days -= _month_days
                if (self.lunarMonth == _leap_month):
                    """ 如果当月还是闰月 """
                    _month_days = _leap_day
                    if (_span_days < _month_days):
                        """ 指定日期在闰月中 ???"""
                        self.lunarMonth = (_leap_month << 4) | self.lunarMonth
                        break
                    """ 否则扣除闰月天数，月份加一 """
                    _span_days -= _month_days
                self.lunarMonth += 1
                _month_days = self.getMonthLeapMonthLeapDays()[0]
            self.lunarDay += _span_days
            return self.lunarYear, self.lunarMonth, self.lunarDay
        else:
            """ 新年前倒推去年日期 """
            self.lunarMonth = 12
            self.lunarYear -= 1
            _month_days, _leap_month, _leap_day = self.getMonthLeapMonthLeapDays()
            while abs(_span_days) > _month_days:
                _span_days += _month_days
                self.lunarMonth -= 1
                if (self.lunarMonth == _leap_month):
                    _month_days = _leap_day
                    if (abs(_span_days) <= _month_days):  # 指定日期在闰月中
                        self.lunarMonth = (_leap_month << 4) | self.lunarMonth
                        break
                    _span_days += _month_days
                _month_days = self.getMonthLeapMonthLeapDays()[0]
            self.lunarDay += (_month_days + _span_days)  # 从月份总数中倒扣 得到天数
            return self.lunarYear, self.lunarMonth, self.lunarDay
    # # # 24节气部分
    def getSolarTermsDateList(self):
        solarTermsList = getTheYearAllSolarTermsList(self.date.year)
        self.solarTermsDateList = []
        for i in range(0, len(solarTermsList)):
            day = solarTermsList[i]
            month = i // 2 + 1
            self.solarTermsDateList.append((month, day))
        return self.solarTermsDateList
    def getNextNum(self,findDate,solarTermsDateList):
        return len(list(filter(lambda y: y <= findDate, solarTermsDateList)))%24
    def get_todaySolarTerms(self):
        '''
        :return:是否节气
        '''
        solarTermsDateList = self.getSolarTermsDateList()
        findDate = (self.date.month, self.date.day)
        nextNum = self.getNextNum(findDate,solarTermsDateList)
        self.nextSolarTerm = solarTermsNameList[nextNum]
        if findDate in solarTermsDateList:
            todaySolarTerm = solarTermsNameList[solarTermsDateList.index(findDate)]
        else:
            todaySolarTerm = '无'
        return todaySolarTerm
    # # # 八字部分
    def get_year8Char(self):
        str=the10HeavenlyStems[(self.lunarYear-4)%10] + the12EarthlyBranches[(self.lunarYear - 4) % 12]
        return str
    # 月八字与节气相关
    def get_month8Char(self):
        findDate = (self.date.month, self.date.day)
        solarTermsDateList=self.getSolarTermsDateList()
        nextNum = self.getNextNum(findDate,solarTermsDateList)
        # 2019年正月为丙寅月
        if nextNum==0 and self.date.month==12:
            nextNum=25
        apartNum=(nextNum+1)//2
        # (year-2019)*12+apartNum每年固定差12个月回到第N年月柱，2019小寒甲子，加上当前过了几个节气除以2+(nextNum-1)//2，减去1
        month8Char=the60HeavenlyEarth[((self.date.year-2019)*12+apartNum)%60]
        return month8Char

    def get_day8Char(self):
        apart=self.date-datetime(2019,1,29)
        baseNum=the60HeavenlyEarth.index('丙寅')
        # 超过23点算第二天，为防止溢出，在baseNum上操作+1
        if self.twohourNum == 12:
            baseNum+=1
        self.dayHeavenlyEarthNum=(apart.days+baseNum)%60
        return the60HeavenlyEarth[self.dayHeavenlyEarthNum]

    def get_twohour8CharList(self):
        # 北京时间离长安时间差1小时，一天24小时横跨13个时辰,清单双循环
        begin = (the60HeavenlyEarth.index(self.day8Char) * 12) % 60
        return (the60HeavenlyEarth + the60HeavenlyEarth)[begin:begin + 13]

    def get_twohour8Char(self):
        return self.twohour8CharList[self.twohourNum]

    def get_the8char(self):
        return self.get_year8Char(),self.get_month8Char(),self.get_day8Char()

    def get_earthNum(self):
        self.yearEarthNum = the12EarthlyBranches.index(self.year8Char[1])
        self.monthEarthNum=the12EarthlyBranches.index(self.month8Char[1])
        self.dayEarthNum=the12EarthlyBranches.index(self.day8Char[1])
        return self.yearEarthNum,self.monthEarthNum,self.dayEarthNum

    def get_heavenNum(self):
        self.yearHeavenNum = the10HeavenlyStems.index(self.year8Char[0])
        self.monthHeavenNum = the10HeavenlyStems.index(self.month8Char[0])
        self.dayHeavenNum = the10HeavenlyStems.index(self.day8Char[0])
        return self.yearHeavenNum,self.monthHeavenNum,self.dayHeavenNum
    # 季节
    def get_season(self):
        self.seasonType= self.monthEarthNum % 3
        self.seasonNum = ((self.monthEarthNum - 2) % 12) // 3
        self.lunarSeason = '仲季孟'[self.seasonType] + '春夏秋冬'[self.seasonNum]
    # 星座
    def get_starZodiac(self):
        n = ('摩羯座', '水瓶座', '双鱼座', '白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', '天秤座', '天蝎座', '射手座')
        d = (
            (1, 20), (2, 19), (3, 21), (4, 21), (5, 21), (6, 22), (7, 23), (8, 23), (9, 23), (10, 23), (11, 23),
            (12, 23))
        return n[len(list(filter(lambda y: y <= (self.date.month, self.date.day), d))) % 12]
    # 节日
    def get_legalHolidays(self):
        temp=''
        if self.todaySolarTerms in legalsolarTermsHolidayDic:
            temp+=legalsolarTermsHolidayDic[self.todaySolarTerms]+' '
        if (self.date.month,self.date.day)in legalHolidaysDic:
            temp+=legalHolidaysDic[(self.date.month,self.date.day)]+' '
        if not self.lunarMonth>12:
            if (self.lunarMonth,self.lunarDay)in legalLunarHolidaysDic:
                temp+=legalLunarHolidaysDic[(self.lunarMonth,self.lunarDay)]
        return temp.strip().replace(' ',',')

    def get_otherHolidays(self):
        tempList,y,m,d,wn,w=[],self.date.year,self.date.month,self.date.day,self.date.isocalendar()[1],self.date.isocalendar()[2]
        eastHolidays={5: (2, 7, '母亲节'), 6: (3, 7, '父亲节')}
        if m in eastHolidays:
            t1dwn=datetime(y,m,1).isocalendar()[1]
            if ((wn-t1dwn+1),w)==(eastHolidays[m][0],eastHolidays[m][1]):
                tempList.append(eastHolidays[m][2])
        holidayDic=otherHolidaysList[m-1]
        if d in holidayDic:
            tempList.append(holidayDic[d])
        if tempList!=[]:
            return ','.join(tempList)
        else:
            return ''
    def get_otherLunarHolidays(self):
        if not self.lunarMonth>12:
            holidayDic = otherLunarHolidaysList[self.lunarMonth - 1]
            if self.lunarDay in holidayDic:
                return holidayDic[self.lunarDay]
        return ''

    # 彭祖百忌
    def get_pengTaboo(self, long=9, delimit=','):
        return pengTatooList[self.dayHeavenNum][:long] + delimit + pengTatooList[self.dayEarthNum + 10][:long]

    # 建除十二神，《淮南子》曰：正月建寅，则寅为建，卯为除，辰为满，巳为平，主生；午为定，未为执，主陷；申为破，主衡；酉为危，主杓；戍为成，主小德；亥为收，主大备；子为开，主太阳；丑为闭，主太阴。
    def get_today12DayOfficer(self):
        thisMonthStartGodNum = (self.lunarMonth - 1 + 2) % 12
        apartnum = self.dayEarthNum - thisMonthStartGodNum
        self.today12DayOfficer = chinese12DayOfficers[apartnum % 12]
        return self.today12DayOfficer
    # 八字与五行
    def get_the28Stars(self):
        apart = self.date - datetime(2019, 1, 17)
        return the28StarsList[apart.days%28]
    def get_nayin(self):
        return theHalf60HeavenlyEarth5ElementsList[the60HeavenlyEarth.index(self.day8Char) // 2]
    def get_today5Elements(self):
        nayin = self.get_nayin()
        tempList = ['天干', self.day8Char[0],
                    '属' + the10HeavenlyStems5ElementsList[self.dayHeavenNum],
                    '地支', self.day8Char[1],
                    '属' + the12EarthlyBranches5ElementsList[self.dayEarthNum],
                    '纳音', nayin[-1], '属' + nayin[-1],
                    '廿八宿', self.today28Star[0],'宿',
                    '十二神', self.today12DayOfficer, '日'
                    ]
        return tempList
    def get_the9FlyStar(self):
        apartNum = (self.date - datetime(2019, 1, 17)).days
        startNumList=[7,3,5,6,8,1,2,4,9]
        flyStarList=[str((i - 1 - apartNum) % 9 + 1) for i in startNumList]
        return ''.join(flyStarList)
    def get_luckyGodsDirection(self):
        todayNum=self.dayHeavenNum
        direction=[
        '喜神'+directionList[chinese8Trigrams.index(luckyGodDirection[todayNum])],
        '财神'+directionList[chinese8Trigrams.index(wealthGodDirection[todayNum])],
        '福神'+directionList[chinese8Trigrams.index(mascotGodDirection[todayNum])],
        '阳贵'+directionList[chinese8Trigrams.index(sunNobleDirection[todayNum])],
        '阴贵'+directionList[chinese8Trigrams.index(moonNobleDirection[todayNum])],
        ]
        return direction
    def get_fetalGod(self):
        return fetalGodList[the60HeavenlyEarth.index(self.day8Char)]
    # 每日时辰凶吉
    def get_twohourLuckyList(self):
        def tmp2List(tmp):
            return ['凶' if tmp & (2 ** (12 - i)) > 0 else '吉' for i in range(1, 13)]
        todayNum=self.dayHeavenlyEarthNum
        tomorrowNum=(self.dayHeavenlyEarthNum+1)%60
        outputList=(tmp2List(twohourLuckyTimeList[todayNum])+tmp2List(twohourLuckyTimeList[tomorrowNum]))
        return outputList[:13]
    # 每日神煞、每日宜忌部分
    def get_today12DaysGod(self):
        '''
        chinese12DayGods=['青龙','明堂','天刑','朱雀','金贵','天德','白虎','玉堂','天牢','玄武','司命','勾陈']
        青龙定位口诀：子午寻申位，丑未戌上亲；寅申居子中，卯酉起于寅；辰戌龙位上，巳亥午中寻。
        [申戌子寅辰午]
        十二神凶吉口诀：道远几时通达，路遥何日还乡 辶为吉神(0,1,4,5,7,11)为黄道吉日
        '''
        num=(self.dayEarthNum-2*(self.monthEarthNum-2))%12
        self.today12DayGod=chinese12DayGods[num]
        dayName ='黄道日' if num in (0,1,4,5,7,11) else '黑道日'
        return self.today12DayGod,dayName
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
        good = {'满': ['嫁娶', '移徙', '求财', '祈福', '祭祀', '出行', '立契', '交易', '开市', '修仓'],
                '成': ['安床', '动土', '移徙', '修造', '嫁娶', '求财', '出行', '栽种', '立契', '竖柱', '安葬', '交易', '开市', '破土'],
                '开': ['安床', '动土', '移徙', '修造', '赴任', '祈福', '宴会', '祭祀', '出行', '求嗣', '入学', '动土', '交易', '开市', '竖柱'],
                '建': ['赴任', '祈福', '求嗣', '安葬', '修造', '上樑', '求财', '入学', '嫁娶', '立契', '交涉', '出行'],
                '除': ['祭祀', '祈福', '嫁娶', '出行', '移徙', '动土', '求医', '交易'],
                '平': ['嫁娶', '修造', '破土', '安葬', '开市', '动土', '求嗣'],
                '定': ['祭祀', '祈福', '嫁娶', '修造', '开市', '赴任'],
                '执': ['修造', '装修', '嫁娶', '立契', '祭祀'], '破': ['破土', '求医'],
                '危': ['祭祀', '祈福', '安床', '破土'],
                '收': ['祈福', '求嗣', '赴任', '嫁娶', '修造', '动土', '交易', '立契'],
                '闭': ['祭祀', '祈福', '埋穴', '安葬', '填补']}
        bad = {'建': ['动土', '开仓', '纳采'],
               '平': ['赴任', '移徙', '进人口', '嫁娶', '祈福', '动土', '纳采', '修造', '竖柱'],
               '收': ['安床', '移徙', '嫁娶', '安葬', '放债', '动土', '纳采', '开市', '修造', '竖柱', '破土'],
               '闭': ['安床', '手术', '移徙', '求医', '嫁娶', '进人口', '出行', '动土', '纳采', '赴任', '开市', '修造', '竖柱', '上梁'],
               '除': ['嫁娶', '赴任', '出行', '立契'], '满': ['安葬', '赴任', '求医'], '定': ['诉讼', '出行', '交涉'],
               '执': ['开市', '求财', '出行', '搬迁'], '破': ['嫁娶', '立契', '交涉', '出行', '搬迁'],
               '危': ['出行', '嫁娶', '安葬', '迁徙'], '成': ['诉讼'], '开': ['放债', '诉讼', '安葬']}
        def defauleThing(o=self.today12DayOfficer):
            dic = {'goodName': [], 'badName': [], 'goodThing': [], 'badThing': []}
            if o in good:
                dic['goodThing'] = good[o]
            if o in bad:
                dic['badThing'] = bad[o]
            return dic
        dic=defauleThing(self.today12DayOfficer)
        bujiang=['壬寅壬辰辛丑辛卯辛巳庚寅庚辰丁丑丁卯丁巳戊寅戊辰','辛丑辛卯庚子庚寅庚辰丁丑丁卯丙子丙寅丙辰戊子戊寅戊辰','辛亥辛丑辛卯庚子庚寅丁亥丁丑丁卯丙子丙寅戊子戊寅','庚戌庚子庚寅丁亥丁丑丙戌丙子丙寅乙亥乙丑戊戌戊子戊寅','丁酉丁亥丁丑丙戌丙子乙酉乙亥乙丑甲戌甲子戊戌戊子','丁酉丁亥丙申丙戌丙子乙酉乙亥甲申甲戌甲子戊申戊戌戊子','丙申丙戌乙未乙酉乙亥甲申甲戌癸未癸酉癸亥戊申戊戌','乙未乙酉甲午甲申甲戌癸未癸酉壬午壬申壬戌戊午戊申戊戌','乙巳乙未乙酉甲午甲申癸巳癸未癸酉壬午壬申戊午戊申','甲辰甲午甲申癸巳癸未壬辰壬午壬申辛巳辛未戊辰戊午戊申','癸卯癸巳癸未壬辰壬午辛卯辛巳辛未庚辰庚午戊辰戊午','癸卯癸巳壬寅壬辰壬午辛卯辛巳庚寅庚辰庚午戊寅戊辰戊午']
        mrY13 = [(1, 13), (2, 11), (3, 9), (4, 7), (5, 5), (6, 2), (7, 1), (7, 29), (8, 27), (9, 25), (10, 23), (11, 21),(12, 19)]
        tomorrow = self.date + timedelta(days=1)
        tmd=(tomorrow.month, tomorrow.day)
        t4l=[self.thisYearSolarTermsDic[i] for i in ['春分', '夏至', '秋分', '冬至']]
        t4j=[self.thisYearSolarTermsDic[i] for i in ['立春', '立夏', '立秋', '立冬']]
        s=self.today28Star
        d=self.day8Char
        den=self.dayEarthNum
        dhen=self.dayHeavenlyEarthNum
        sn=self.seasonNum
        # st=self.seasonType
        yhn=self.yearHeavenNum
        yen=self.yearEarthNum
        men=self.monthEarthNum
        ldn=self.lunarDay
        lmn=self.lunarMonth

        angel = [
            ('岁德', '甲庚丙壬戊甲庚丙壬戊'[yhn], d, ['修造', '动土', '嫁娶', '纳采', '移徙', '入宅']),
            # 岁德、岁德合：年天干对日天干['修造','动土','嫁娶','纳采','移徙','入宅','百事皆宜'] 天干相合+5  20190206
            ('岁德合', '己乙辛丁癸己乙辛丁癸'[yhn], d, ['修造', '动土', '赴任', '嫁娶', '纳采', '移徙', '入宅', '出行']),  # 修营、起土，上官。嫁娶、远行，参谒
            ('月德', '壬庚丙甲'[men % 4], d[0], ['赴任', '谒贵', '求贤', '修造', '动土', '嫁娶', '移徙', '纳财', '买畜', '立券']),
            # 月德20190208《天宝历》曰：“月德者，月之德神也。取土、修营宜向其方，宴乐、上官利用其日。
            ('月德合', '丁乙辛己'[men % 4], d[0], ['上书', '祭祀', '修造', '动土', '赴任', '出行', '嫁娶', '移徙', '开市', '纳财', '纳畜', '种植'],
             ['诉讼']),
            ('天德', '巳庚丁申壬辛亥甲癸寅丙乙'[men], d,
             ['嫁娶', '祭祀', '修造', '上书', '动土', '祈福', '入宅', '安葬', '订婚', '六礼', '宴会', '纳采', '修仓', '栽种', '求医', '赴任', '雪冤',
              '竖柱']),  # 天德'巳庚丁申壬辛亥甲癸寅丙乙'天德合'申乙壬巳丁丙寅己戊亥辛庚'
            ('天德合', '空乙壬空丁丙空己戊空辛庚'[men], d,
             ['嫁娶', '祭祀', '修造', '上书', '动土', '祈福', '入宅', '安葬', '订婚', '六礼', '宴会', '纳采', '修仓', '栽种', '求医', '赴任', '雪冤',
              '竖柱']),
            ('凤凰日', s[0], '危昴胃毕'[sn], ['嫁娶']),
            ('麒麟日', s[0], '井尾牛壁'[sn], []),  # 凤凰日、麒麟日（麒麟日测试日期2019.03.07）
            ('四相', d[0], ('丙丁', '戊己', '壬癸', '甲乙')[sn],
             ['祭祀', '赴任', '订婚', '嫁娶', '修作', '移徙', '种植', '出行', '上官', '纳采', '造宅', '修造', '上梁']),
            # 《总要历》曰：“四相者，四时王相之辰也。其日宜修营、起工、养育，生财、栽植、种莳、移徙、远行，曰：“春丙丁，夏戊己，秋壬癸，冬甲乙。
            ('不将', d, bujiang[men], ['嫁娶', '订婚', '招赘', '纳婿']),
            ('时德', '午辰子寅'[sn], d[1], ['祈福', '宴请', '求职', '谒贵']),  # 时德:春午 夏辰 秋子 冬寅 20190204
            ('大葬', d, '壬申癸酉壬午甲申乙酉丙申丁酉壬寅丙午己酉庚申辛酉', ['安葬']),
            ('鸣吠', d, '庚午壬申癸酉壬午甲申乙酉己酉丙申丁酉壬寅丙午庚寅庚申辛酉', ['安葬', '开光', '破土', '启攒', '成服', '除服', '附葬']),
            ('小葬', d, '庚午壬辰甲辰乙巳甲寅丙辰庚寅', ['安葬']),
            # ('鸣吠对', d, '丙寅丁卯丙子辛卯甲午庚子癸卯壬子甲寅乙卯', ['安葬']),
            ('鸣吠对', d, '丙寅丁卯丙子辛卯甲午庚子癸卯壬子甲寅乙卯', ['安葬', '破土', '启攒', '成服', '除服', '修坟', '开光']),  # （改）
            ('不守塚', d, '庚午辛未壬申癸酉戊寅己卯壬午癸未甲申乙酉丁未甲午乙未丙申丁酉壬寅癸卯丙午戊申己酉庚申辛酉', ['破土']),
            ('官日', '卯午酉子'[sn], d[1], ['赴任']),
            ('民日', '午酉子卯'[sn], d[1], []),
            ('天贵', d[0], ('甲乙', '丙丁', '庚辛', '壬癸')[sn], []),  # 20190216
            ('天喜', '申酉戌亥子丑寅卯辰巳午未'[men], d[1], ['嫁娶', '纳采', '求嗣', '祈福', '订婚', '入宅', '开市', '造宅']),
            ('天富', '寅卯辰巳午未申酉戌亥子丑'[men], d, ['造葬', '作仓']),
            ('天恩', dhen % 15 < 5 and dhen // 15 != 2, [True], ['动土']),
            ('三合', (den - men) % 4 == 0, [True], []),  # 三合数在地支上相差4个顺位
            ('六合', '丑子亥戌酉申未午巳辰卯寅'[men], d, ['祈福', '嫁娶', '订婚', '开市', '入宅', '造葬']),
            # ('月恩', '甲辛丙丁庚己戊辛壬癸庚乙'[men], d, ['营造', '婚姻', '移徙', '祭祀', '上官', '纳财', '动土']),#《五行论》曰：“月恩者，阳建所生之干也，子母相从谓之月恩。其日宜营造，婚姻、移徙，祭祀，上官，纳财。”
            ('月恩', '甲辛丙丁庚己戊辛壬癸庚乙'[men], d, ['营造', '移徙', '祭祀', '上官', '纳财', '动土', '祈福', '斋醮', '订婚', '嫁娶', '造葬', '修造']),
            ('天成', '卯巳未酉亥丑卯巳未酉亥丑'[men], d, []),
            ('天官', '午申戌子寅辰午申戌子寅辰'[men], d, []),
            ('天医', '亥子丑寅卯辰巳午未申酉戌'[men], d, ['求医', '合药', '针灸', '服药']),  # 《总要历》曰：“天医者，人之巫医。其日宜请药，避病、寻巫、祷祀。
            ('天马', '寅辰午申戌子寅辰午申戌子'[men], d, ['出行', '移居', '入宅', '开市', '求财', '营商']),  # （改）
            ('天财', '子寅辰午申戌子寅辰午申戌'[men], d, []),
            ('地财', '丑卯巳未酉亥丑卯巳未酉亥'[men], d, ['入财']),
            ('月财', '酉亥午巳巳未酉亥午巳巳未'[men], d, ['开市', '作仓', '作灶', '移徙', '出行', '移徙']),  # 起造、出行、移居
            # ('月空', '丙甲壬庚丙甲壬庚丙甲壬庚'[men], d, ['上书', '陈策', '造床', '修屋', '动土']),#《天宝历》曰：“月中之阳辰也。所理之日宜设筹谋。陈计策。
            ('月空', '丙甲壬庚丙甲壬庚丙甲壬庚'[men], d, ['上书', '陈策', '造床', '修造', '斋醮']),  # 《天宝历》曰：“月中之阳辰也。所理之日宜设筹谋。陈计策。#（改）
            ('母仓', d[1], ('亥子', '寅卯', '辰丑戌未', '申酉')[sn], ['种植', '畜牧', '纳财', '祈福', '许愿', '开光', '订婚', '嫁娶', '起造', '修仓']),
            ('明星', '辰午甲戌子寅辰午甲戌子寅'[men], d, ['赴任', '诉讼', '造葬']),
            ('圣心', '辰戌亥巳子午丑未寅申卯酉'[men], d, ['祭祀', '祀神', '斋醮', '祈福', '功果', '嫁娶']),
            ('五富', '巳申亥寅巳申亥寅巳申亥寅'[men], d, []),
            ('禄库', '寅卯辰巳午未申酉戌亥子丑'[men], d, ['纳财']),
            ('福生', '寅申酉卯戌辰亥巳子午丑未'[men], d, ['祭祀', '祈福', '斋醮', '入宅', '求财']),
            ('福厚', '寅巳申亥'[sn], d, []),
            ('吉庆', '未子酉寅亥辰丑午卯申巳戌'[men], d, []),
            ('阴德', '丑亥酉未巳卯丑亥酉未巳卯'[men], d, ['祭祀', '斋醮', '施恩', '行惠', '功果']),
            ('活曜', '卯申巳戌未子酉寅亥辰丑午'[men], d, []),
            ('解神', '午午申申戌戌子子寅寅辰辰'[men], d, ['讼狱', '解冤', '上表', '词讼', '解除', '沐浴', '整容', '剃头', '修甲', '求医']),
            ('生气', '戌亥子丑寅卯辰巳午未申酉'[men], d, ['修造', '种植', '安床', '移徒', '治病', '求嗣', '嫁娶', '订婚']),
            ('普护', '丑卯申寅酉卯戌辰亥巳子午'[men], d, ['祈福', '嫁娶', '出行', '求医', '斋醮', '出行', '移徒']),
            ('益后', '巳亥子午丑未寅申卯酉辰戌'[men], d, ['嫁娶', '立嗣']),
            ('续世', '午子丑未寅申卯酉辰戌巳亥'[men], d, ['嫁娶', '立嗣', '祭祀', '祈福', '求嗣', '订婚', '嫁娶', '修作', '造葬']),
            ('要安', '未丑寅申卯酉辰戌巳亥午子'[men], d, ['嫁娶', '订婚', '求财', '修方', '造葬']),
            ('驿马', '寅亥申巳寅亥申巳寅亥申巳'[men], d, ['出行', '上官', '赴任', '经商', '求财', '开市', '移徙']),
            ('天愿', '甲子癸未甲午甲戌乙酉丙子丁丑戊午甲寅丙辰辛卯戊辰'[men], d,
             ['求财', '出行', '嫁娶', '祈福', '祭祀', '求嗣', '斋醮', '订婚', '兴修', '修坟', '造葬']),  # 天愿日，以月之干支为依据，择与之和合之日为是，故为月之喜神
            ('临日', '辰酉午亥申丑戌卯子巳寅未'[men], d, ['祭祀', ',上册', '入学', '出行', '赴任']),  # 正月午日、二月亥日、三月申日、四月丑日等为临日
            ('天后', '寅亥申巳寅亥申巳寅亥申巳'[men], d, ['求医', '针灸', '服药']),
            ('天仓', '辰卯寅丑子亥戌酉申未午巳'[men], d, ['订婚', '嫁娶', '牧养', '纳财', '纳畜', '起造', '修仓', '纳财']),
            # 《总要历》曰:天仓者,天库之神也。其日可以修仓库、受赏赐、纳财、牧养。《历例》曰:天仓者,正月起寅,逆行十二辰。
            ('敬安', '子午未丑申寅酉卯戌辰亥巳'[men], d, ['求职', '赴任']),  # 恭顺之神当值
            ('玉宇', '申寅卯酉辰戌巳亥午子未丑'[men], d, []),
            ('金堂', '酉卯辰戌巳亥午子未丑申寅'[men], d, []),

        ]
        demon = [
            ('岁破', den == (yen + 6) % 12, [True], ['修造', '移徙', '嫁娶', '出行']),
            # 《广圣历》曰：“岁破者，太岁所冲之辰也。其地不可兴造、移徙，嫁娶、远行，犯者主损财物及害家长，惟战伐向之吉。
            ('天罡', '卯戌巳子未寅酉辰亥午丑申'[men], d, ['动土']),
            ('月厌', '子亥戌酉申未午巳辰卯寅丑'[men], d,
             ['祈福', '求嗣', '上表', '颁诏', '施恩', '诏命', '招贤', '布政', '庆赐', '赏贺', '宴会', '冠带', '遣使', '安抚', '选将', '出师',
              '赴任', '临政', '纳采', '嫁娶', '进人', '搬移', '远回', '安床', '解除', '整容', '剃头', '修甲', '求医', '裁制', '营建', '修造', '动土',
              '竖柱上梁', '修仓库', '鼓铸', '经络', '酝酿', '开市', '立券', '交易', '纳财', '开仓', '出货', '修置', '开渠', '安碓', '塞穴', '修墙', '平道',
              '破屋', '伐木', '栽种', '牧养', '纳畜', '破土', '安葬', '启攒']),
            ('厌对', '午巳辰卯寅丑子亥戌酉申未'[men], d, ['嫁娶', '出行']),
            ('河魁', '酉辰亥午丑申卯戌巳子未寅'[men], d, ['起造', '动土', '安门']),
            # ('勾绞', '酉辰亥午丑申卯戌巳子未寅'[men], d, []),
            ('小红砂', '酉丑巳酉丑巳酉丑巳酉丑巳'[men], d, ['嫁娶']),
            ('人隔。', '丑亥酉未巳卯丑亥酉未巳卯'[men], d, ['嫁娶', '进人']),
            ('往亡', '戌丑寅巳申亥卯午酉子辰未'[men], d,
             ['出行', '赴任', '嫁娶', '求谋', '求财', '上表', '颁诏', '诏命', '招贤', '布政', '遣使', '安抚', '选将', '出师', '临政', '进人',
              '搬移', '求医', '捕捉', '畋猎', '取鱼']),
            ('重丧', '癸己甲乙己丙丁己庚辛己壬'[men], d, ['嫁娶', '动土', '安葬']),
            ('重复', '癸己庚辛己壬癸戊甲乙己壬'[men], d, ['嫁娶', '安葬']),
            ('杨公忌', (lmn, ldn), mrY13, ['开张', '动土', '嫁娶', '立券']),  # 杨筠松根据“二十八星宿”顺数，订定了“杨公十三忌”
            ('神号', '申酉戌亥子丑寅卯辰巳午未'[men], d, []),
            ('妨择', '辰辰午午申申戌戌子子寅寅'[men], d, []),
            ('披麻', '午卯子酉午卯子酉午卯子酉'[men], d, ['嫁娶', '入宅']),
            ('冰消瓦陷', '酉辰巳子丑申卯戌亥午未寅'[men], d, ['修造']),
            ('大耗', '辰巳午未申酉戌亥子丑寅卯'[men], d, ['修仓', '纳财']),  # 历例曰：“大耗者，岁中虚耗之神也。所理之地不可营造仓库、纳财物
            ('天吏', '卯子酉午卯子酉午卯子酉午'[men], d,
             ['祈福', '求嗣', '上表', '诏命', '招贤', '冠带', '遣使', '安抚', '选将', '出师', '赴任', '临政', '嫁娶', '进人', '搬移', '安床', '解除',
              '求医', '修造', '动土', '竖柱', '修仓', '开市', '立券', '交易', '纳财', '开仓', '出货', '修置', '栽种', '牧养', '纳畜']),
            ('天瘟', '丑卯未戌辰寅午子酉申巳亥'[men], d, ['修造', '治病', '六畜', '修造']),
            ('天狱', '午酉子卯午酉子卯午酉子卯'[men], d, ['封章', '词讼', '赴任', '征讨']),
            ('天火', '午酉子卯午酉子卯午酉子卯'[men], d, ['修造', '入宅', '苫盖']),
            ('天棒', '寅辰午申戌子寅辰午申戌子'[men], d, ['诉讼']),
            ('天狗', '寅卯辰巳午未申酉戌亥子丑'[men], d, ['祭祀']),
            ('天狗下食', '戌亥子丑寅卯辰巳午未申酉'[men], d, ['祭祀']),
            ('天贼', '卯寅丑子亥戌酉申未午巳辰'[men], d, ['安葬', '出行', '开池', '动土', '竖造', '入宅', '开仓', '遣使', '修仓', '出货']),
            ('地火', '子亥戌酉申未午巳辰卯寅丑'[men], d, ['栽种', '修园']),
            ('独火', '未午巳辰卯寅丑子亥戌酉申'[men], d, ['作灶', '修造']),
            ('月破', '午未申酉戌亥子丑寅卯辰巳'[men], d,
             ['修造', '大事勿用', '祈福', '求嗣', '上表', '颁诏', '诏命', '招贤', '布政', '庆赐', '赏贺', '宴会', '冠带', '遣使', '安抚', '选将', '出师',
              '赴任', '临政', '纳采', '嫁娶', '进人', '搬移', '安床', '整容', '剃头', '修甲', '裁制', '修造', '动土', '竖柱', '修仓', '鼓铸', '经络',
              '酝酿', '立券', '交易', '纳财', '开仓', '出货', '修置', '开渠', '安碓', '塞穴', '修墙', '伐木', '栽种', '牧养', '纳畜', '破土', '安葬',
              '启攒']),
            ('月杀月虚', '未辰丑戌未辰丑戌未辰丑戌'[men], d, ['造门']),
            ('受死', '卯酉戌辰亥巳子午丑未寅申'[men], d, [], ['捕猎']),
            ('死气', '辰巳午未申酉戌亥子丑寅卯'[men], d, ['修造', '安床']),
            ('黄沙', '寅子午寅子午寅子午寅子午'[men], d, ['出行']),
            ('六不成', '卯未寅午戌巳酉丑申子辰亥'[men], d, ['修造']),
            ('小耗', '卯辰巳午未申酉戌亥子丑寅'[men], d, ['修仓', '开市', '立券', '交易', '纳财', '开仓', '出货', '栽种']),
            ('神隔', '酉未巳卯丑亥酉未巳卯丑亥'[men], d, ['祭祀', '祈福']),
            ('朱雀', '亥丑卯巳未酉亥丑卯巳未酉'[men], d, ['入宅', '开门']),
            ('白虎', '寅辰午申戌子寅辰午申戌子'[men], d, ['安葬']),
            ('玄武', '巳未酉亥丑卯巳未酉亥丑卯'[men], d, ['安葬']),
            ('勾陈', '未酉亥丑卯巳未酉亥丑卯巳'[men], d, []),
            ('木马', '辰午巳未酉申戌子亥丑卯寅'[men], d, []),
            ('五鬼', '未戌午寅辰酉卯申丑巳子亥'[men], d, ['出行']),
            ('破败', '辰午申戌子寅辰午申戌子寅'[men], d, []),
            ('殃败', '巳辰卯寅丑子亥戌酉申未午'[men], d, []),
            ('雷公', '巳申寅亥巳申寅亥巳申寅亥'[men], d, []),
            ('飞廉', '申酉戌巳午未寅卯辰亥子丑'[men], d, ['纳畜', '修造', '动土', '移徙', '嫁娶']),
            # 《神枢经》曰：“飞廉者，岁之廉察使君之象，亦名大煞。所理之不可兴工、动土，移徙，嫁娶《广圣历》曰：“子年在申，丑年在酉，寅年在戌，卯年在巳，辰年在午，巳年在未，午年在寅，未年在卯，申 年在辰，酉年在亥，戌年在子，亥年在丑也。”
            ('枯鱼', '申巳辰丑戌未卯子酉午寅亥'[men], d, ['栽种']),
            ('九空', '申巳辰丑戌未卯子酉午寅亥'[men], d, ['出行', '求财', '开仓', '种植', '进人', '开仓', '修仓', '开市', '立券', '交易', '纳财', '出货']),
            ('八座', '酉戌亥子丑寅卯辰巳午未申'[men], d, []),
            ('血忌', '午子丑未寅申卯酉辰戌巳亥'[men], d, ['针灸', '纳畜', '刺血', '阉割', '六畜', '穿鼻']),
            ('阴错', '壬子癸丑庚寅辛卯庚辰丁巳丙午丁未甲申乙酉甲戌癸亥'[men * 2:men * 2 + 2], d, ['赴任']),
            ('三娘煞', ldn, (3, 7, 13, 18, 22, 27), ['嫁娶']),
            ('月忌', ldn, (5, 14, 23), ['出游', '入宅', '行船']),
            ('四绝日', tmd, t4j, ['出行', '赴任', '嫁娶', '进人', '迁移', '开市', '立券', '祭祀']),
            ('四离日', tmd, t4l, ['出行', '嫁娶']),
            # 天转有四日，分别是春季的乙卯日，夏季的丙午日，秋季的辛酉日，冬季的壬子日。
            # 地转也有四日，分别是春季的辛卯日，夏季的戊午日，秋季的癸酉日，冬季的丙子日。
            # “春季乙辛到兔位，夏天丙戊马上求；秋来辛癸听鸡叫，冬寒丙壬鼠洞留”。
            ('天转', '乙卯丙午辛酉壬子'[sn * 2:sn * 2 + 2], d, ['动土', '修造', '搬家', '嫁娶']),
            ('地转', '辛卯戊午癸酉丙子'[sn * 2:sn * 2 + 2], d, ['动土', '修造', '搬家', '嫁娶']),
            ('月建转杀', '卯午酉子'[sn], d, ['动土', '修造']),
            ('荒芜', d[1], '巳酉丑申子辰亥卯未寅午戌'[sn * 3:sn * 3 + 3], []),
            # ('四正废', d, '庚申辛酉壬子癸亥甲寅乙卯丙午丁巳'[sn * 4:sn * 4 + 4], ['修造', '交易', '安床']),
            ('四废', d, ('庚申辛酉', '壬子癸亥', '甲寅乙卯', '丁巳丙午')[sn], ['修造', '交易', '安床']),  # 庚申辛酉为春废，壬子癸亥夏时当。甲寅乙卯秋月值，丁巳丙午冬季防。
            ('蚩尤', '戌子寅辰午申'[men % 6], d, ['冠笄']),  # 正七逢寅二八辰，三九午上四十申。五十一月原在戌，六十二月子为真。
            ('大时', '酉午卯子酉午卯子酉午卯子'[men], d,
             ['祈福', '求嗣', '上表', '颁诏', '施恩', '诏命', '招贤', '冠带', '遣使', '安抚', '选将', '出师', '赴任', '临政', '纳采', '嫁娶', '进人',
              '搬移', '安床', '解除', '求医', '营建', '修造', '竖柱', '修仓', '开市', '立券', '交易', '纳财', '开仓', '出货', '修置', '栽种', '牧养',
              '纳畜']),
            # 《神枢经》曰:大时者,将军之象也。所直之日,忌出军攻战、筑室会亲。李鼎祚曰:大时者,正月起卯逆行四仲。
            ('大败', '酉午卯子酉午卯子酉午卯子'[men], d,
             ['祈福', '求嗣', '上表', '颁诏', '施恩', '诏命', '招贤', '冠带', '遣使', '安抚', '选将', '出师', '赴任', '临政', '纳采', '嫁娶', '进人',
              '搬移', '安床', '解除', '求医', '营建', '修造', '竖柱', '修仓', '开市', '立券', '交易', '纳财', '开仓', '出货', '产室', '栽种', '牧养',
              '纳畜', '出行', '营谋', '求婚']),
            # 十恶大败干支纪日分别为：甲辰、乙巳、丙申、丁亥、戊戌、己丑、庚辰、辛巳、壬申、癸亥。（不确定）《总要历》曰:大败者,兵败忌辰也。其日忌临阵侵敌、攻城野战。《历例》曰:正月起卯,逆行四仲。
            ('五虚', '午戌巳酉丑申子辰亥卯未寅'[men], d, ['修仓', '开仓', '出货', '闻张', '闻库', '闻铺', '闻店']),
            # 《枢要历》曰:五虛者,四时绝辰也。其日忌开仓、营种莳、出财宝、放债负。《历例》曰:五虚者,春巳酉丑,夏申子辰,秋亥卯未,冬寅午戌也。
            ('咸池', '酉午卯子酉午卯子酉午卯子'[men], d, ['嫁娶', '取鱼', '乘船']),  # 《历例》曰:咸池者,正月起卯,逆行四仲;
            ('土符', '申子丑巳酉寅午戌卯未亥辰'[men], d,
             ['营建', '修造', '修仓', '修置', '开渠', '安碓', '补垣', '修墙', '平道', '破屋', '栽种', '破土', '起造']),
            # 《历例》曰:士符者,正月丑，二月已,三月酉,四月寅,五月午,六月戌,七月卯,八月未,九月亥,十月辰,十一月申,十二月子。
            ('四击', '未未戌戌戌丑丑丑辰辰辰未'[men], d, ['上官', '远行', '出军', '嫁娶', '进人', '迁移', '安抚', '选将', '出师']),
            # 四击者,春戌、夏丑、秋辰、冬未。按四击者,四时所冲之墓辰也。如正二三月建寅卯辰,辰与戌冲,故戌为四击也。馀仿此。
            ('九坎', '申巳辰丑戌未卯子酉午寅亥'[men], d, ['种植', '修造', '破土', '塞穴', '取鱼', '乘船']),
            # 《广圣历》曰:九坎者,月中杀神也。其日忌乘船渡水、修堤防、筑垣墙、苫盖屋舍。《历例》曰:九坎者,正月在辰逆行四季,五月在卯逆行四仲,九月在寅逆行四孟。
            ('九焦', '申巳辰丑戌未卯子酉午寅亥'[men], d, ['种植', '修造', '破土', '塞穴', '取鱼', '乘船']),
            # 《广圣历》曰:九焦者,月中杀神也。其日忌炉冶、铸造、种植、修筑园圃。《历例》曰:正月在辰逆行四季,五月在卯逆行四仲,九月在寅逆行四孟。
            ('游祸', '亥申巳寅亥申巳寅亥申巳寅'[men], d, ['求医', '祭祀', '祈福', '求嗣', '解除']),
            # 官历宜服药?  《神枢经》曰:游祸者,月中恶神也。其日忌服药请医、祀神致祭。李鼎祚曰:游祸者,正月起已逆行四孟。
            ('归忌', '寅子丑寅子丑寅子丑寅子丑'[men], d, ['远回', '入宅', '归火', '嫁娶', '搬移']),
            # 《广圣历》:归忌者,月内凶神也。其日忌远行、归家移徙、娶归、《历例》曰:孟月丑,仲月寅,季月子
            ('复日', '癸巳甲乙戊丙丁巳庚辛戊壬'[men], d, ['安葬', '修坟', '破土', '启攒', '入殓', '移柩', '除服']),
            # 《天宝历》曰:复日者,为魁罡所系之辰也。其日忌为凶事,利为吉事。《历例》曰:复日者,正、七月甲庚,二、八月乙辛,四十月丙壬,五、十一月丁癸,三、九、六、十二月戊巳日也。
            ('月害', '未午巳辰卯寅丑子亥戌酉申'[men], d,
             ['祈福', '求嗣', '上表', '庆赐', '赏贺', '宴会', '安抚', '选将', '出师', '纳采', '嫁娶', '进人', '求医', '修仓', '经络', '酝酿', '开市',
              '立券', '交易', '纳财', '开仓', '出货', '修置', '牧养', '纳畜', '破土', '安葬', '启攒']),
            ('月刑', '卯戌巳子辰申午丑寅酉未亥'[men], d,
             ['祈福', '求嗣', '上表', '颁诏', '施恩', '诏命', '招贤', '布政', '庆赐', '赏贺', '宴会', '冠带', '遣使', '安抚', '训兵', '出师', '赴任',
              '临政', '纳采', '嫁娶', '进人', '搬移', '安床', '解除', '整容', '剃头', '修甲', '求医', '裁制', '营建', '修造', '竖柱', '修仓', '鼓铸',
              '经络', '酝酿', '开市', '立券', '交易', '纳财', '开仓', '出货', '修置', '开渠', '安碓', '塞穴', '修墙', '破屋', '栽种', '牧养', '纳畜',
              '破土', '安葬', '启攒']),
            ('大煞', '申酉戌巳午未寅卯辰亥子丑'[men], d, [])
        ]


        def getTodayGoodBadThing():
            for i in [(angel,'goodName','goodThing'),(demon, 'badName', 'badThing')]:
                y,y1,y2=i[0],i[1],i[2]
                for x in y:
                    if x[1] in x[2]:
                        dic[y1] += [x[0]]
                        dic[y2] += x[3]
                dic[y2]=list(set(dic[y2]))
            # 宜忌抵消
            for i in dic['goodThing']:
                if i in dic['badThing']:
                    dic['goodThing'].remove(i)
                    dic['badThing'].remove(i)
            # 宜忌抵消后相克，岁德、月德、凤凰麒麟压朱雀白虎、三丧、月破、岁破、重丧、天罡等
            # 待补充
            for i in angel[:2]:
                if i[0] in dic['goodName']:
                    dic['goodThing']=list(set(dic['goodThing']+i[3]))
                    for j in i[3]:
                        dic['badThing'].remove(j)
            # 排序
            def sortCollation(x):
                sortList=['出行','嫁娶', '开市','祭祀', '祈福', '动土']
                if x in sortList:
                    return sortList.index(x)
                return len(sortList)+1
            dic['goodThing'].sort(key=sortCollation)
            dic['badThing'].sort(key=sortCollation)
        getTodayGoodBadThing()
        return (dic['goodName'],dic['badName']),(dic['goodThing'],dic['badThing'])