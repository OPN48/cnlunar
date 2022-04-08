# 工具拓展模块
# author: cuba3
# github: https://github.com/OPN48/pyLunarCalendar

# 去除空行
from cnlunar.config import ENC_VECTOR_LIST, thingsSort

def rfRemove(l=[],removeList=[]):
    for removeThing in list(set(l).intersection(set(removeList))):
        l.remove(removeThing)
    return l
def rfAdd(l=[],addList=[]):
    return list(set(l+addList))

def not_empty(s):
    return s and s.strip()

# 两个List合并对应元素相加或者相减，a[i]+b[i]:tpye=1 a[i]-b[i]:tpye=-1
def abListMerge(a, b=ENC_VECTOR_LIST, type=1):
    c = []
    for i in range(len(a)):
        c.append(a[i]+b[i]*type)
    return c

def sortCollation(x, sortList=thingsSort):
    if x in sortList:
        return sortList.index(x)
    else:
        return len(sortList) + 1