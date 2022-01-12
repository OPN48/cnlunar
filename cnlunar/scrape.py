# coding=gbk
# coding=UTF-8
# 数据爬虫模块
# author: cuba3
# github: https://github.com/OPN48/pyLunarCalendar
from cnlunar.solar24 import zipSolarTermsList
from cnlunar.tools import not_empty

# 爬虫获取香港天文台数据
def hkweather(year):
    import requests
    url='http://data.weather.gov.hk/gts/time/calendar/text/T'+str(year)+'c.txt'
    r = requests.get(url)
    r.encoding = 'Big5'
    temp=r.text.replace('  ',',').replace(',,',',')
    return temp.split('\n')[3:]
# 年区间获取，数据清洗
def getHkWeather(beginYear=1901,endYear=2100):
    outputDataList=[]
    for year in range(beginYear,endYear+1):
        print('正在获取公元%i年二十四节气' % year)
        tempList=hkweather(year)
        modelList=['date','lunarDate','week','solarTerms']
        yearSolarTermsList=[]
        for line in tempList:
            lineTemp=list(filter(not_empty, line.split(',')))
            dic=dict(zip(modelList,lineTemp))
            try:
                dic['solarTerms']=dic['solarTerms'].strip() or ''
                if dic['solarTerms'].strip():
                    dateTemp = dic['date'].replace('年', '-').replace('月', '-').replace('日', '').split('-')
                    yearSolarTermsList.append(int(dateTemp[2]))
            except:
                pass
        print('获取完成' + str(yearSolarTermsList))
        outputDataList.append(zipSolarTermsList(yearSolarTermsList)[0])
    return outputDataList
