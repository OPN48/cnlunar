# pyGregorian2LunarCalendar
前言：
由于三体运动（主要地球、太阳、月球）无法准确预测，目前二十四节气依然还是靠天文台观测，Yovey使用传说中[Y*D+C]-L方法实际有很多天数不准，def getSolarTerms(_date)12个if嵌套判断让代码变得十分冗余，由简书网友“大咖_247c”首先发现计算不准问题……
方案过程： 1、在校验过数据与公式差异后，第一方案是采用15%黄经夹角计算，计算后差异依然存在，地球椭圆形轨道一年内公转速度差异超过7%；
2、在发现椭圆轨道问题后，尝试使用平均值、开普勒第二定律计算行星轨道，计算值已经十分贴近了，但依然和香港天文台数据有差异，恍然大悟，地球、月亮、太阳三个天体呈现无法完美预测的三体运动，甚至还包括木星引力影响（比如传说中九星连珠，虽然引力抵消微弱），而且太阳本身也在运动，地球和太阳的质量也不是永恒不变的，这就导致地球的恒星年相对稳定，但回归年浮动振荡；
3、当试过所有技术物理原理还无法调节误差后，最终使用了Chen Jian的核心设计理念，添加了十六进制加存二十四节气。
# coding=UTF-8 # 1901~2100年农历数据表
# Author: cuba3 # base code by Yovey , https://www.jianshu.com/p/8dc0d7ba2c2a
# powered by Late Lee, http://www.latelee.org/python/python-yangli-to-nongli.html#comment-78
# other author:Chen Jian, http://www.cnblogs.com/chjbbs/p/5704326.html
# 数据来源: http://data.weather.gov.hk/gts/time/conversion1_text_c.htm
