import datetime, cnlunar
import json
from flask import Flask, jsonify, request, send_from_directory
from prettytable import PrettyTable

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# http://localhost:5000/lunar_info?date=2022-2-3-10_30&type=1
@app.route('/lunar_info', methods=['GET'])
def get_lunar_info_api():
    date_string = request.args.get('date')
    lunar_type = request.args.get('type', default=1, type=int)
    if date_string:
        try:
            year, month, day, time_str = date_string.split('-')
            hour, minute = map(int, time_str.split('_'))
            test_date = datetime.datetime(int(year), int(month), int(day), hour, minute)
            result = get_lunar_info_json(test_date, lunar_type)
        except ValueError:
            result = json.dumps({
                'code': 4,
                'msg': '无效的日期参数'
            }, ensure_ascii=False, indent=4)
    else:
        result = json.dumps({
            'code': 3,
            'msg': '缺少date参数'
        }, ensure_ascii=False, indent=4)
    response = app.response_class(
        response=result,
        status=200,
        mimetype='application/json'
    )
    return response

# 计算农历信息
def get_lunar_info(date, lunar_type = 1):
    try:
        if (lunar_type == 1):
            version = '八字月柱与八字日柱算神煞版本'
            lunar = cnlunar.Lunar(date, godType='8char')
        else:
            version = '八字立春切换算法'
            lunar = cnlunar.Lunar(date, godType='8char', year8Char='beginningOfSpring')
        
        return {
            'code': 0,
            'msg': 'ok',
            'data': {
                'version': version,
                '日期': lunar.date.strftime('%Y年%m月%d日 %H:%M'),
                '农历数字': (lunar.lunarYear, lunar.lunarMonth, lunar.lunarDay, '闰' if lunar.isLunarLeapMonth else ''),
                '农历': f'{lunar.lunarYearCn} {lunar.year8Char}[{lunar.chineseYearZodiac}]年 {lunar.lunarMonthCn}{lunar.lunarDayCn}',
                '星期': lunar.weekDayCn,
                # 未增加除夕
                '今日节日': (lunar.get_legalHolidays(), lunar.get_otherHolidays(), lunar.get_otherLunarHolidays()),
                '八字': f'{lunar.year8Char} {lunar.month8Char} {lunar.day8Char} {lunar.twohour8Char}',
                '今日节气': lunar.todaySolarTerms,
                '下一节气': (lunar.nextSolarTerm, lunar.nextSolarTermDate, lunar.nextSolarTermYear),
                '今年节气表': lunar.thisYearSolarTermsDic,
                '季节': lunar.lunarSeason,

                '今日时辰': lunar.twohour8CharList,
                '时辰凶吉': lunar.get_twohourLuckyList(),
                '生肖冲煞': lunar.chineseZodiacClash,
                '星座': lunar.starZodiac,
                '星次': lunar.todayEastZodiac,

                '彭祖百忌': lunar.get_pengTaboo(),
                '彭祖百忌精简': lunar.get_pengTaboo(long=4, delimit='<br>'),
                '十二神': lunar.get_today12DayOfficer(),
                '廿八宿': lunar.get_the28Stars(),

                '今日三合': lunar.zodiacMark3List,
                '今日六合': lunar.zodiacMark6,
                '今日五行': lunar.get_today5Elements(),

                '纳音': lunar.get_nayin(),
                '九宫飞星': lunar.get_the9FlyStar(),
                '吉神方位': lunar.get_luckyGodsDirection(),
                '今日胎神': lunar.get_fetalGod(),
                '神煞宜忌': lunar.angelDemon,
                '今日吉神': lunar.goodGodName,
                '今日凶煞': lunar.badGodName,
                '宜忌等第': lunar.todayLevelName,
                '宜': lunar.goodThing,
                '忌': lunar.badThing,
                '时辰经络': lunar.meridians
            }
        }
    except Exception as e:
        print(f"获取农历信息失败: {e}")
        return {
            'code': 1,
            'msg': '获取农历信息失败: {e}'
        }

# 转换为json
def get_lunar_info_json(date, lunar_type = 1):
    lunar_info = get_lunar_info(date, lunar_type)
    if lunar_info:
        return json.dumps(lunar_info, ensure_ascii=False, indent=4)
    else:
        return json.dumps({
            'code': 2,
            'msg': '获取农历信息失败'
        }, ensure_ascii=False, indent=4)
    
# 命令行调试输出成表格
def print_lunar_info(lunar_info, type = 'table'):
    if not lunar_info:
        return

    if type == 'table':
        table = PrettyTable()
        table.field_names = ['字段', '值']
        for key, value in lunar_info.items():
            table.add_row([key, value])

        print(table)
    else:
        for i in lunar_info:
            midstr = '\t' * (2 - len(i) // 2) + ':' + '\t'
            print(i, midstr, lunar_info[i])

    return



# 测试日期
# test_date = datetime.datetime(1992, 1, 16, 10, 35)

# 获取并打印农历信息
# lunar_info = get_lunar_info(test_date, 1)
# if lunar_info['code'] != 0:
#     print(lunar_info['msg'])
#     exit(1)
# print_lunar_info(lunar_info.get('data'))


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
