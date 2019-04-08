# pyGregorian2LunarCalendar
# coding=UTF-8
# 1901~2100年农历数据表
# author: cuba3, github: https://github.com/cuba3/pyGregorian2LunarCalendar
# base code by Yovey , https://www.jianshu.com/p/8dc0d7ba2c2a
# powered by Late Lee, http://www.latelee.org/python/python-yangli-to-nongli.html#comment-78
# other author:Chen Jian, http://www.cnblogs.com/chjbbs/p/5704326.html
# 数据来源: http://data.weather.gov.hk/gts/time/conversion1_text_c.htm


from datetime import datetime,timedelta
from config import *
from solar24 import getTheYearAllSolarTermsList

class Lunar():
    def __init__(self,date=datetime.now()):
        self.date = date
        self._upper_year = ''
        (self.lunarYear, self.lunarMonth, self.lunarDay) = self.get_lunarDateNum()
        (self.lunarYearCn,self.lunarMonthCn,self.lunarDayCn)=self.get_lunarCn()
        self.twohour8CharList = self.get_twohour8CharList()
        (self.year8Char, self.month8Char, self.day8Char, self.twohour8Char) = self.get_the8char()
        self.chineseYearZodiac=self.get_chineseYearZodiac()
        self.chineseZodiacClash=self.get_chineseZodiacClash()
        self.weekDayCn=self.get_weekDayCn()
        self.todaySolarTerms=self.get_todaySolarTerms()
        self.thisYearSolarTermsDic=dict(zip(solarTermsNameList, self.solarTermsDateList))
    #大写农历年、月、日
    def get_lunarYearCN(self):
        for i in str(self.lunarYear):
            self._upper_year += upperNum[int(i)]
        return self._upper_year
    def get_lunarMonthCN(self):

        leap = (self.lunarMonth >> 4) & 0xf
        m = self.lunarMonth & 0xf
        lunarMonth = lunarMonthNameList[(m - 1) % 12]
        if leap == m:
            lunarMonth = "闰" + lunarMonth
        return lunarMonth
    def get_lunarCn(self):
        return self.get_lunarYearCN(), self.get_lunarMonthCN(), lunarDayNameList[(self.lunarDay - 1) % 30]
    # 生肖
    def get_chineseYearZodiac(self):
        return chineseZodiacNameList[(self.lunarYear - 4) % 12]
    def get_chineseZodiacClash(self):
        zodiacNum=the12EarthlyBranches.index(self.day8Char[1])
        zodiacClashNum=(zodiacNum+ 6) % 12
        self.zodiacWin=chineseZodiacNameList[zodiacNum]
        self.zodiacLose=chineseZodiacNameList[zodiacClashNum]
        return self.zodiacWin+'日冲'+self.zodiacLose
    # 星期
    def get_weekDayCn(self):
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
        return [month_day, leap_month, leap_day]
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
            _month_days, _leap_month, _leap_day = self.getMonthLeapMonthLeapDays(self.lunarYear, self.lunarMonth)
            while abs(_span_days) > _month_days:
                _span_days += _month_days
                self.lunarMonth -= 1
                if (self.lunarMonth == _leap_month):
                    _month_days = _leap_day
                    if (abs(_span_days) <= _month_days):  # 指定日期在闰月中
                        self.lunarMonth = (_leap_month << 4) | self.lunarMonth
                        break
                    _span_days += _month_days
                _month_days = self.getMonthLeapMonthLeapDays(self.lunarYear, self.lunarMonth)[0]
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
        :param date: 输入日期
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
        return the60HeavenlyEarth[((self.date.year-2019)*12+apartNum)%60]
    def get_day8Char(self):
        apart=self.date-datetime(2019,1,29)
        baseNum=the60HeavenlyEarth.index('丙寅')
        dayNum=(apart.days+baseNum)%60
        return the60HeavenlyEarth[dayNum]
    def get_twohour8CharList(self):
        apart = (self.date - datetime(2019, 1, 2)).days % 5
        # 北京时间离长安时间差1小时，一天24小时横跨13个时辰,清单双循环
        return (the60HeavenlyEarth+the60HeavenlyEarth)[apart*12:(apart*12+13)]
    def get_twohour8Char(self):
        num=(self.date.hour+1)//2
        return self.twohour8CharList[num]
    def get_the8char(self):
        return self.get_year8Char(),self.get_month8Char(),self.get_day8Char(),self.get_twohour8Char()
    # 彭祖百忌
    def get_pengTaboo(self):
        return pengTatooList[the10HeavenlyStems.index(self.day8Char[0])] + ' ' + pengTatooList[
            the12EarthlyBranches.index(self.day8Char[1]) + 10]
    # 建除十二神，正月建寅，二月建卯……
    def get_today12Gods(self):
        thisMonthStartGodNum=(self.lunarMonth-1+2)%12
        apartnum=the12EarthlyBranches.index(self.day8Char[1])-thisMonthStartGodNum
        return chinese12Gods[apartnum%12]
    # 星座
    def get_starZodiac(self):
        n = ('摩羯座', '水瓶座', '双鱼座', '白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', '天秤座', '天蝎座', '射手座')
        d = (
            (1, 20), (2, 19), (3, 21), (4, 21), (5, 21), (6, 22), (7, 23), (8, 23), (9, 23), (10, 23), (11, 23),
            (12, 23))
        return n[len(list(filter(lambda y: y <= (self.date.month, self.date.day), d))) % 12]
