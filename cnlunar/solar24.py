# 24节气模块\节气数据16进制加解密
# author: cuba3
# github: https://github.com/OPN48/pyLunarCalendar

from cnlunar.config import SOLAR_TERMS_DATA_LIST, START_YEAR
from cnlunar.tools import abListMerge

# 解压缩16进制用
def unZipSolarTermsList(data,rangeEndNum=24,charCountLen=2):
    list2 = []
    for i in range(1,rangeEndNum+1):
        right = charCountLen * (rangeEndNum-i)
        if type(data).__name__=='str':
            data= int(data, 16)
        x=data >> right
        c=2**charCountLen
        list2=[(x % c)]+list2
    return abListMerge(list2)
# 采集压缩用
def zipSolarTermsList(inputList,charCountLen=2):
    tempList=abListMerge(inputList, type=-1)
    data=0
    num=0
    for i in tempList:
        data+=i << charCountLen*num
        num+=1
    return hex(data),len(tempList)

def getTheYearAllSolarTermsList(year):
    return unZipSolarTermsList(SOLAR_TERMS_DATA_LIST[year - START_YEAR])

