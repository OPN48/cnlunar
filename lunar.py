# pyGregorian2LunarCalendar
# coding=UTF-8
# 1901~2100年农历数据表
# author: cuba3, github: https://github.com/cuba3/pyGregorian2LunarCalendar
# base code by Yovey , https://www.jianshu.com/p/8dc0d7ba2c2a
# powered by Late Lee, http://www.latelee.org/python/python-yangli-to-nongli.html#comment-78
# other author:Chen Jian, http://www.cnblogs.com/chjbbs/p/5704326.html
# 数据来源: http://data.weather.gov.hk/gts/time/conversion1_text_c.htm


from datetime import datetime
from config import *
# from config import solarTermsNameList, _cn_month_list, lunarNewYearList, the10HeavenlyStems, the12EarthlyBranches, \
#     chineseZodiacNameList, lunarMonthNameList, \
#     START_YEAR,month_DAY_BIT,month_NUM_BIT,\
#     lunarDayNameList, upperNum, weekDay
from solar24 import getTheYearAllSolarTermsList



def _cnDay(_day):
    """ 农历-日
        Arg:
            type(_day) int 1 数字形式的阴历-日
        Return:
            String "初一"
    """
    return lunarDayNameList[(_day - 1) % 30]
def _cnMonth(_month):
    """ 农历-月
        Arg:
            type(_day) int 13 数字形式的阴历-月
        Return:
            String "闰正月"
    """

    leap = (_month >> 4) & 0xf
    m = _month & 0xf
    _month = lunarMonthNameList[(m - 1) % 12]
    if leap == m:
        _month = "闰" + _month
    return _month


def _cnYear(_year):
    """ 农历-年
        Arg:
            type(_year) int 2018 数字形式的年份
        Return:
            String "戊戍[狗]" 汉字形式的年份
    """
    return the10HeavenlyStems[(_year - 4) % 10] + the12EarthlyBranches[(_year - 4) % 12] + '[' + chineseZodiacNameList[(_year - 4) % 12] + ']'


def getUpperLunarYear(year):

    _upper_year = ""
    for i in str(year):
        _upper_year += upperNum[int(i)]
    return _upper_year


def getUpperWeek(_date):
    """ 星期大写 如：星期一 """

    return weekDay[_date.weekday()]


def getMonthLeapMonthLeapDays(_cn_year, _cn_month):
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
    tmp = lunarMonthData[_cn_year - START_YEAR] # 获取16进制数据12-1月份农历日数 0=29天 1=30天
    # 表示获取当前月份的布尔值:指定二进制1（假定真），向左移动月数-1，与当年全年月度数据合并取出2进制位作为判断
    if tmp & (1 << (_cn_month - 1)):
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


def _getNumCnDate(_date):
    """ 获取数字形式的农历日期
        Args:
            _date = datetime(year, month, day)
        Return:
            _year, _month, _day
            返回的月份，高4bit为闰月月份，低4bit为其它正常月份
    """

    _year, _month, _day = _date.year, 1, 1
    _code_year = lunarNewYearList[_year - START_YEAR]
    """ 获取当前日期与当年春节的差日 """
    _span_days = (_date - datetime(_year, ((_code_year >> 5) & 0x3), ((_code_year >> 0) & 0x1f))).days
    # print("span_day: ", _span_days)

    if (_span_days >= 0):
        """ 新年后推算日期，差日依序减月份天数，直到不足一个月，剪的次数为月数，剩余部分为日数 """
        """ 先获取闰月 """
        _month_days, _leap_month, _leap_day = getMonthLeapMonthLeapDays(_year, _month)
        while _span_days >= _month_days:
            """ 获取当前月份天数，从差日中扣除 """
            _span_days -= _month_days
            if (_month == _leap_month):
                """ 如果当月还是闰月 """
                _month_days = _leap_day
                if (_span_days < _month_days):
                    """ 指定日期在闰月中 ???"""
                    _month = (_leap_month << 4) | _month
                    break
                """ 否则扣除闰月天数，月份加一 """
                _span_days -= _month_days
            _month += 1
            _month_days = getMonthLeapMonthLeapDays(_year, _month)[0]
        _day += _span_days
        return _year, _month, _day
    else:
        """ 新年前倒推去年日期 """
        _month = 12
        _year -= 1
        _month_days, _leap_month, _leap_day = getMonthLeapMonthLeapDays(_year, _month)
        while abs(_span_days) > _month_days:
            _span_days += _month_days
            _month -= 1
            if (_month == _leap_month):
                _month_days = _leap_day
                if (abs(_span_days) <= _month_days):  # 指定日期在闰月中
                    _month = (_leap_month << 4) | _month
                    break
                _span_days += _month_days
            _month_days = getMonthLeapMonthLeapDays(_year, _month)[0]
        _day += (_month_days + _span_days)  # 从月份总数中倒扣 得到天数
        return _year, _month, _day
def getCnDate(_date):
    # 存在1、2月将农历腊月归于今年的输出错误
    """ 获取完整的农历日期
        Args:
            _date = datetime(year, month, day)
        Return:
            "农历 xx[x]年 xxxx年x月xx 星期x"
    """
    (_year, _month, _day) = _getNumCnDate(_date)
    print(_year, _month, _day)
    return "农历 %s年 %s年%s%s %s " % (_cnYear(_year), getUpperLunarYear(_year), _cnMonth(_month), _cnDay(_day), getUpperWeek(_date))


def getCnYear(_date):
    """ 获取农历年份
        Args:
            _date = datetime(year, month, day)
        Return:
            "x月"
    """
    _year = _getNumCnDate(_date)[0]
    return "%s年" % _cnYear(_year)


def getCnMonth(_date):
    """ 获取农历月份
        Args:
            _date = datetime(year, month, day)
        Return:
            "xx"
    """
    _month = _getNumCnDate(_date)[1]
    return "%s" % _cnMonth(_month)


def getCnDay(_date):
    """ 获取农历日
        Args:
            _date = datetime(year, month, day)
        Return:
            "农历 xx[x]年 xxxx年x月xx 星期x"
    """
    _day = _getNumCnDate(_date)[2]
    return "%s" % _cnDay(_day)

def getSolarTerms(date):
    '''
    :param date: 输入日期
    :return:{'今天': '清明', '谷雨': (4, 20)}
    '''
    year=date.year
    inputMonth=date.month
    inputday=date.day
    solarTermsList = getTheYearAllSolarTermsList(year)
    solarTermsDateList = []
    for i in range(0, len(solarTermsList)):
        day = solarTermsList[i]
        month = i // 2 + 1
        solarTermsDateList.append((month, day))
    findDate = (inputMonth, inputday)
    nextNum = len(list(filter(lambda y: y <= findDate , solarTermsDateList))) % 24
    nextSolarTerm = solarTermsNameList[nextNum]
    if findDate in solarTermsDateList:
        todaySolarTerm = solarTermsNameList[solarTermsDateList.index(findDate)]
    else:
        todaySolarTerm = '无'
    return todaySolarTerm,{nextSolarTerm:solarTermsDateList[nextNum]}


def showMonth(date):
    """ 测试：
        输出农历日历
    """
    print(date)
    print(getCnDate(date))  # 根据数组索引确定农历日期
    print(getCnYear(date)) # 返回干支年
    print(getCnMonth(date))  # 返回农历月
    # print(getCnDay(date))  # 返回农历日
    # print(getSolarTerms(date))  # 返回节气
    # print(getUpperYear(date))  # 返回大写年份
    # print(getUpperWeek(date))  # 返回大写星期