# -*- coding: utf-8 -*-
"""
传统八字排盘脚本（完整精确版）

功能：
1.  公历出生时间转四柱：年柱、月柱、日柱、时柱（精确天文节气）
2.  天干地支五行、阴阳
3.  十神
4.  地支藏干（本气/中气/余气）
5.  五行统计
6.  天干五合、地支六合、三合、三会、六冲、六害、三刑
7.  十二长生
8.  日主强弱（旺相休囚死 + 五行力量）
9.  喜用神建议
10. 大运方向 + 精确起运年龄 + 大运列表
11. 纳音、空亡、神煞、胎元、命宫、流年
"""

import argparse
import math
from datetime import datetime, timedelta


# ============================================================
# 基础数据
# ============================================================

GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

GAN_WUXING = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

ZHI_WUXING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

GAN_YINYANG = {
    "甲": "阳", "乙": "阴", "丙": "阳", "丁": "阴", "戊": "阳",
    "己": "阴", "庚": "阳", "辛": "阴", "壬": "阳", "癸": "阴",
}

ZHI_YINYANG = {
    "子": "阳", "丑": "阴", "寅": "阳", "卯": "阴",
    "辰": "阳", "巳": "阴", "午": "阳", "未": "阴",
    "申": "阳", "酉": "阴", "戌": "阳", "亥": "阴",
}

# 地支藏干（本气 / 中气 / 余气）
CANG_GAN = {
    "子": [("癸", "本气")],
    "丑": [("己", "本气"), ("癸", "中气"), ("辛", "余气")],
    "寅": [("甲", "本气"), ("丙", "中气"), ("戊", "余气")],
    "卯": [("乙", "本气")],
    "辰": [("戊", "本气"), ("乙", "中气"), ("癸", "余气")],
    "巳": [("丙", "本气"), ("戊", "中气"), ("庚", "余气")],
    "午": [("丁", "本气"), ("己", "中气")],
    "未": [("己", "本气"), ("丁", "中气"), ("乙", "余气")],
    "申": [("庚", "本气"), ("壬", "中气"), ("戊", "余气")],
    "酉": [("辛", "本气")],
    "戌": [("戊", "本气"), ("辛", "中气"), ("丁", "余气")],
    "亥": [("壬", "本气"), ("甲", "中气")],
}

# 仅天干列表（兼容旧接口）
CANG_GAN_ONLY = {k: [g for g, _ in v] for k, v in CANG_GAN.items()}

# 五行生克
GENERATE = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROL  = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# 天干五合
GAN_HE = {
    ("甲", "己"): "土", ("乙", "庚"): "金", ("丙", "辛"): "水",
    ("丁", "壬"): "木", ("戊", "癸"): "火",
}

# 地支六合
ZHI_LIUHE = {
    ("子", "丑"): "土", ("寅", "亥"): "木", ("卯", "戌"): "火",
    ("辰", "酉"): "金", ("巳", "申"): "水", ("午", "未"): "土",
}

# 地支三合
ZHI_SANHE = {
    ("申", "子", "辰"): "水", ("亥", "卯", "未"): "木",
    ("寅", "午", "戌"): "火", ("巳", "酉", "丑"): "金",
}

# 地支三会
ZHI_SANHUI = {
    ("亥", "子", "丑"): "水", ("寅", "卯", "辰"): "木",
    ("巳", "午", "未"): "火", ("申", "酉", "戌"): "金",
}

# 地支六冲
ZHI_CHONG = {
    ("子", "午"), ("丑", "未"), ("寅", "申"),
    ("卯", "酉"), ("辰", "戌"), ("巳", "亥"),
}

# 地支六害
ZHI_HAI = {
    ("子", "未"), ("丑", "午"), ("寅", "巳"),
    ("卯", "辰"), ("申", "亥"), ("酉", "戌"),
}

# 地支三刑（含自刑）
ZHI_XING_SAN = {("寅", "巳", "申"), ("丑", "戌", "未")}   # 无恩之刑、恃势之刑
ZHI_XING_SHUANG = {("子", "卯")}                           # 无礼之刑
ZHI_XING_ZI = {"辰", "午", "酉", "亥"}                     # 自刑

# 十二长生表（阳干顺行、阴干逆行）
CHANGSHENG = {
    "甲": {"亥": "长生", "子": "沐浴", "丑": "冠带", "寅": "临官",
           "卯": "帝旺", "辰": "衰",   "巳": "病",   "午": "死",
           "未": "墓",   "申": "绝",   "酉": "胎",   "戌": "养"},
    "乙": {"午": "长生", "巳": "沐浴", "辰": "冠带", "卯": "临官",
           "寅": "帝旺", "丑": "衰",   "子": "病",   "亥": "死",
           "戌": "墓",   "酉": "绝",   "申": "胎",   "未": "养"},
    "丙": {"寅": "长生", "卯": "沐浴", "辰": "冠带", "巳": "临官",
           "午": "帝旺", "未": "衰",   "申": "病",   "酉": "死",
           "戌": "墓",   "亥": "绝",   "子": "胎",   "丑": "养"},
    "丁": {"酉": "长生", "申": "沐浴", "未": "冠带", "午": "临官",
           "巳": "帝旺", "辰": "衰",   "卯": "病",   "寅": "死",
           "丑": "墓",   "子": "绝",   "亥": "胎",   "戌": "养"},
    "戊": {"寅": "长生", "卯": "沐浴", "辰": "冠带", "巳": "临官",
           "午": "帝旺", "未": "衰",   "申": "病",   "酉": "死",
           "戌": "墓",   "亥": "绝",   "子": "胎",   "丑": "养"},
    "己": {"酉": "长生", "申": "沐浴", "未": "冠带", "午": "临官",
           "巳": "帝旺", "辰": "衰",   "卯": "病",   "寅": "死",
           "丑": "墓",   "子": "绝",   "亥": "胎",   "戌": "养"},
    "庚": {"巳": "长生", "午": "沐浴", "未": "冠带", "申": "临官",
           "酉": "帝旺", "戌": "衰",   "亥": "病",   "子": "死",
           "丑": "墓",   "寅": "绝",   "卯": "胎",   "辰": "养"},
    "辛": {"子": "长生", "亥": "沐浴", "戌": "冠带", "酉": "临官",
           "申": "帝旺", "未": "衰",   "午": "病",   "巳": "死",
           "辰": "墓",   "卯": "绝",   "寅": "胎",   "丑": "养"},
    "壬": {"申": "长生", "酉": "沐浴", "戌": "冠带", "亥": "临官",
           "子": "帝旺", "丑": "衰",   "寅": "病",   "卯": "死",
           "辰": "墓",   "巳": "绝",   "午": "胎",   "未": "养"},
    "癸": {"卯": "长生", "寅": "沐浴", "丑": "冠带", "子": "临官",
           "亥": "帝旺", "戌": "衰",   "酉": "病",   "申": "死",
           "未": "墓",   "午": "绝",   "巳": "胎",   "辰": "养"},
}

# 月令旺相休囚死（月支 → 各五行状态）
# 旺：同月令  相：月令所生  休：生月令  囚：克月令  死：月令所克
WANG_XIANG = {
    "寅": {"旺": "木", "相": "火", "休": "水", "囚": "金", "死": "土"},
    "卯": {"旺": "木", "相": "火", "休": "水", "囚": "金", "死": "土"},
    "巳": {"旺": "火", "相": "土", "休": "木", "囚": "水", "死": "金"},
    "午": {"旺": "火", "相": "土", "休": "木", "囚": "水", "死": "金"},
    "申": {"旺": "金", "相": "水", "休": "土", "囚": "火", "死": "木"},
    "酉": {"旺": "金", "相": "水", "休": "土", "囚": "火", "死": "木"},
    "亥": {"旺": "水", "相": "木", "休": "金", "囚": "土", "死": "火"},
    "子": {"旺": "水", "相": "木", "休": "金", "囚": "土", "死": "火"},
    "辰": {"旺": "土", "相": "金", "休": "火", "囚": "木", "死": "水"},
    "戌": {"旺": "土", "相": "金", "休": "火", "囚": "木", "死": "水"},
    "丑": {"旺": "土", "相": "金", "休": "火", "囚": "木", "死": "水"},
    "未": {"旺": "土", "相": "金", "休": "火", "囚": "木", "死": "水"},
}

# 旺相休囚死 → 权重
WX_WEIGHT = {"旺": 2.0, "相": 1.5, "休": 0.8, "囚": 0.5, "死": 0.3}

# 纳音六十甲子
NAYIN = {
    "甲子": "海中金", "乙丑": "海中金", "丙寅": "炉中火", "丁卯": "炉中火",
    "戊辰": "大林木", "己巳": "大林木", "庚午": "路旁土", "辛未": "路旁土",
    "壬申": "剑锋金", "癸酉": "剑锋金", "甲戌": "山头火", "乙亥": "山头火",
    "丙子": "涧下水", "丁丑": "涧下水", "戊寅": "城头土", "己卯": "城头土",
    "庚辰": "白蜡金", "辛巳": "白蜡金", "壬午": "杨柳木", "癸未": "杨柳木",
    "甲申": "泉中水", "乙酉": "泉中水", "丙戌": "屋上土", "丁亥": "屋上土",
    "戊子": "霹雳火", "己丑": "霹雳火", "庚寅": "松柏木", "辛卯": "松柏木",
    "壬辰": "长流水", "癸巳": "长流水", "甲午": "砂中金", "乙未": "砂中金",
    "丙申": "山下火", "丁酉": "山下火", "戊戌": "平地木", "己亥": "平地木",
    "庚子": "壁上土", "辛丑": "壁上土", "壬寅": "金箔金", "癸卯": "金箔金",
    "甲辰": "覆灯火", "乙巳": "覆灯火", "丙午": "天河水", "丁未": "天河水",
    "戊申": "大驿土", "己酉": "大驿土", "庚戌": "钗钏金", "辛亥": "钗钏金",
    "壬子": "桑柘木", "癸丑": "桑柘木", "甲寅": "大溪水", "乙卯": "大溪水",
    "丙辰": "沙中土", "丁巳": "沙中土", "戊午": "天上火", "己未": "天上火",
    "庚申": "石榴木", "辛酉": "石榴木", "壬戌": "大海水", "癸亥": "大海水",
}

# 空亡（日柱旬空）
KONGWANG = {
    "甲子": ("戌", "亥"), "乙丑": ("戌", "亥"), "丙寅": ("戌", "亥"),
    "丁卯": ("戌", "亥"), "戊辰": ("戌", "亥"), "己巳": ("戌", "亥"),
    "庚午": ("戌", "亥"), "辛未": ("戌", "亥"), "壬申": ("戌", "亥"),
    "癸酉": ("戌", "亥"),
    "甲戌": ("申", "酉"), "乙亥": ("申", "酉"), "丙子": ("申", "酉"),
    "丁丑": ("申", "酉"), "戊寅": ("申", "酉"), "己卯": ("申", "酉"),
    "庚辰": ("申", "酉"), "辛巳": ("申", "酉"), "壬午": ("申", "酉"),
    "癸未": ("申", "酉"),
    "甲申": ("午", "未"), "乙酉": ("午", "未"), "丙戌": ("午", "未"),
    "丁亥": ("午", "未"), "戊子": ("午", "未"), "己丑": ("午", "未"),
    "庚寅": ("午", "未"), "辛卯": ("午", "未"), "壬辰": ("午", "未"),
    "癸巳": ("午", "未"),
    "甲午": ("辰", "巳"), "乙未": ("辰", "巳"), "丙申": ("辰", "巳"),
    "丁酉": ("辰", "巳"), "戊戌": ("辰", "巳"), "己亥": ("辰", "巳"),
    "庚子": ("辰", "巳"), "辛丑": ("辰", "巳"), "壬寅": ("辰", "巳"),
    "癸卯": ("辰", "巳"),
    "甲辰": ("寅", "卯"), "乙巳": ("寅", "卯"), "丙午": ("寅", "卯"),
    "丁未": ("寅", "卯"), "戊申": ("寅", "卯"), "己酉": ("寅", "卯"),
    "庚戌": ("寅", "卯"), "辛亥": ("寅", "卯"), "壬子": ("寅", "卯"),
    "癸丑": ("寅", "卯"),
    "甲寅": ("子", "丑"), "乙卯": ("子", "丑"), "丙辰": ("子", "丑"),
    "丁巳": ("子", "丑"), "戊午": ("子", "丑"), "己未": ("子", "丑"),
    "庚申": ("子", "丑"), "辛酉": ("子", "丑"), "壬戌": ("子", "丑"),
    "癸亥": ("子", "丑"),
}


# ============================================================
# 精确节气计算（天文算法，基于 Jean Meeus 公式）
# ============================================================

def _sun_longitude(jd: float) -> float:
    """计算给定儒略日的太阳视黄经（度，0-360），精度约 0.01°"""
    T = (jd - 2451545.0) / 36525.0

    # 太阳平黄经
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
    L0 %= 360.0

    # 太阳平近点角
    M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
    M %= 360.0
    M_rad = math.radians(M)

    # 中心差
    C = ((1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M_rad)
         + (0.019993 - 0.000101 * T) * math.sin(2.0 * M_rad)
         + 0.000289 * math.sin(3.0 * M_rad))

    sun_lon = L0 + C

    # 章动修正
    omega = 125.04 - 1934.136 * T
    sun_lon -= 0.00569 - 0.00478 * math.sin(math.radians(omega))

    return sun_lon % 360.0


def _solar_term_jd(year: int, angle: float) -> float:
    """
    计算指定年份指定太阳黄经角度对应的儒略日。
    angle: 太阳黄经度数（0=春分, 15=清明, ..., 315=立春, 345=惊蛰）
    """
    # 将角度归一化到 [-180, 180)，确保初始估计在正确年份
    norm_angle = angle if angle <= 180.0 else angle - 360.0

    # 初始估计：春分约在 3 月 20 日（一年中的第 79 天左右）
    days_from_j2000 = (year - 2000) * 365.2422
    est_jd = 2451545.0 + days_from_j2000 + 79.0 + norm_angle * 365.2422 / 360.0

    # 牛顿迭代求精
    for _ in range(30):
        sl = _sun_longitude(est_jd)
        diff = angle - sl
        if diff > 180.0:
            diff -= 360.0
        elif diff < -180.0:
            diff += 360.0
        if abs(diff) < 0.00001:
            break
        est_jd += diff * 1.015

    return est_jd


def _jd_to_datetime(jd: float) -> datetime:
    """儒略日 → 北京时间 datetime"""
    jd += 0.5
    Z = int(jd)
    F = jd - Z

    if Z < 2299161:
        A = Z
    else:
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - int(alpha / 4)

    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)

    day_val = B - D - int(30.6001 * E) + F
    if E < 14:
        month = E - 1
    else:
        month = E - 13
    if month > 2:
        year_val = C - 4716
    else:
        year_val = C - 4715

    day_int = int(day_val)
    frac = day_val - day_int
    hour = int(frac * 24)
    minute = int((frac * 24 - hour) * 60)
    second = int(((frac * 24 - hour) * 60 - minute) * 60)

    dt_utc = datetime(year_val, month, day_int, hour, minute, second)
    return dt_utc + timedelta(hours=8)


# 十二"节"（月柱分界）对应的太阳黄经
_JIE_ANGLES = [
    (315, "立春"), (345, "惊蛰"), (15,  "清明"),
    (45,  "立夏"), (75,  "芒种"), (105, "小暑"),
    (135, "立秋"), (165, "白露"), (195, "寒露"),
    (225, "立冬"), (255, "大雪"), (285, "小寒"),
]

# 角度 → 月支
_ANGLE_TO_MONTH_ZHI = {
    315: "寅", 345: "卯", 15:  "辰", 45:  "巳",
    75:  "午", 105: "未", 135: "申", 165: "酉",
    195: "戌", 225: "亥", 255: "子", 285: "丑",
}


def get_jie_times(year: int) -> list:
    """
    返回该年 12 个"节"的 (datetime, 月支) 列表，按时间排序。
    包含上一年的小寒（约1月）到本年的小寒（约次年1月）。
    """
    result = []
    for angle, name in _JIE_ANGLES:
        jd = _solar_term_jd(year, angle)
        dt = _jd_to_datetime(jd)
        result.append((dt, _ANGLE_TO_MONTH_ZHI[angle], name))
    result.sort(key=lambda x: x[0])
    return result


def get_lichun(year: int) -> datetime:
    """获取指定年的立春 datetime"""
    jd = _solar_term_jd(year, 315)
    return _jd_to_datetime(jd)


# ============================================================
# 四柱计算
# ============================================================

def year_ganzhi(dt: datetime) -> str:
    """年柱：以精确立春为界"""
    lichun = get_lichun(dt.year)
    year = dt.year if dt >= lichun else dt.year - 1
    offset = year - 1984
    return GAN[offset % 10] + ZHI[offset % 12]


def month_zhi_by_date(dt: datetime) -> str:
    """月支：以精确"节"为界"""
    # 获取本年及上一年的节（小寒跨年）
    jie_times = get_jie_times(dt.year)
    # 加上上一年的小寒
    prev_jie = get_jie_times(dt.year - 1)
    all_jie = [j for j in prev_jie if j[0].year < dt.year] + jie_times

    # 找到 dt 所在的月
    for i in range(len(all_jie) - 1):
        if all_jie[i][0] <= dt < all_jie[i + 1][0]:
            return all_jie[i][1]
    # 如果 dt 在最后一个节之后（小寒之后），属于该节对应的月
    return all_jie[-1][1]


def month_ganzhi(dt: datetime, year_gan: str) -> str:
    """月柱：月干五虎遁"""
    first_month_gan_map = {
        "甲": "丙", "己": "丙",
        "乙": "戊", "庚": "戊",
        "丙": "庚", "辛": "庚",
        "丁": "壬", "壬": "壬",
        "戊": "甲", "癸": "甲",
    }
    month_order = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]
    month_zhi = month_zhi_by_date(dt)
    first_gan = first_month_gan_map[year_gan]
    offset = month_order.index(month_zhi)
    month_gan = GAN[(GAN.index(first_gan) + offset) % 10]
    return month_gan + month_zhi


def day_ganzhi(dt: datetime) -> str:
    """日柱：以 1900-01-31（甲子日）为基准推算"""
    base = datetime(1900, 1, 31)
    delta = (dt.date() - base.date()).days
    return GAN[delta % 10] + ZHI[delta % 12]


def hour_ganzhi(dt: datetime, day_gan: str) -> str:
    """时柱：五鼠遁"""
    hour = dt.hour
    # 子时: 23:00–00:59, 丑时: 01:00–02:59, ...
    if hour == 23:
        zhi_index = 0
    else:
        zhi_index = ((hour + 1) // 2) % 12
    hour_zhi = ZHI[zhi_index]

    first_hour_gan_map = {
        "甲": "甲", "己": "甲",
        "乙": "丙", "庚": "丙",
        "丙": "戊", "辛": "戊",
        "丁": "庚", "壬": "庚",
        "戊": "壬", "癸": "壬",
    }
    first_gan = first_hour_gan_map[day_gan]
    hour_gan = GAN[(GAN.index(first_gan) + zhi_index) % 10]
    return hour_gan + hour_zhi


# ============================================================
# 起运年龄（精确算法）
# ============================================================

def calc_qiyun_age(dt: datetime, year_gan: str, month_pillar: str, gender: str) -> float:
    """
    精确计算起运年龄。
    阳男阴女 → 顺数到下一个"节"的天数
    阴男阳女 → 逆数到上一个"节"的天数
    3 天 = 1 岁
    """
    yy = GAN_YINYANG[year_gan]
    shun = (gender == "male" and yy == "阳") or (gender == "female" and yy == "阴")

    # 获取所有节
    jie_times = get_jie_times(dt.year)
    prev_jie = get_jie_times(dt.year - 1)
    all_jie = [j for j in prev_jie if j[0].year < dt.year] + jie_times

    if shun:
        # 顺行：找到出生后的下一个节
        for jt in all_jie:
            if jt[0] > dt:
                days = (jt[0] - dt).total_seconds() / 86400.0
                return days / 3.0
    else:
        # 逆行：找到出生前的上一个节
        for i in range(len(all_jie) - 1, -1, -1):
            if all_jie[i][0] < dt:
                days = (dt - all_jie[i][0]).total_seconds() / 86400.0
                return days / 3.0

    return 8.0  # fallback


# ============================================================
# 十神
# ============================================================

def get_shishen(day_gan: str, other_gan: str) -> str:
    """十神判断"""
    me = GAN_WUXING[day_gan]
    other = GAN_WUXING[other_gan]
    same_yy = GAN_YINYANG[day_gan] == GAN_YINYANG[other_gan]

    if me == other:
        return "比肩" if same_yy else "劫财"
    if GENERATE[me] == other:
        return "食神" if same_yy else "伤官"
    if CONTROL[me] == other:
        return "偏财" if same_yy else "正财"
    if CONTROL[other] == me:
        return "七杀" if same_yy else "正官"
    if GENERATE[other] == me:
        return "偏印" if same_yy else "正印"
    return "未知"


# ============================================================
# 分析模块
# ============================================================

def split_pillar(pillar: str):
    return pillar[0], pillar[1]


def wuxing_count(pillars: list) -> dict:
    """
    五行力量统计：
    天干权重 1.0
    地支本气权重 1.0
    地支中气权重 0.6
    地支余气权重 0.3
    """
    WEIGHT_MAP = {"本气": 1.0, "中气": 0.6, "余气": 0.3}
    count = {"木": 0.0, "火": 0.0, "土": 0.0, "金": 0.0, "水": 0.0}

    for pillar in pillars:
        gan, zhi = split_pillar(pillar)
        count[GAN_WUXING[gan]] += 1.0

        for hidden_gan, depth in CANG_GAN[zhi]:
            count[GAN_WUXING[hidden_gan]] += WEIGHT_MAP[depth]

    return count


def day_master_strength(day_gan: str, month_zhi: str, count: dict) -> tuple:
    """
    精确日主强弱判断，综合：
    1. 月令旺相休囚死
    2. 五行力量统计
    3. 通根情况
    """
    me = GAN_WUXING[day_gan]
    ws = WANG_XIANG[month_zhi]

    # 找出日主五行在月令的状态
    wx_state = None
    for state, wx in ws.items():
        if wx == me:
            wx_state = state
            break

    score = 0.0

    # 月令旺相休囚死加权
    score += WX_WEIGHT[wx_state] * 3.0

    # 同五行力量
    score += count[me] * 1.2

    # 生我者
    support = None
    for k, v in GENERATE.items():
        if v == me:
            support = k
            break
    score += count.get(support, 0) * 0.8

    # 我生者
    output = GENERATE[me]
    score -= count.get(output, 0) * 0.5

    # 我克者
    wealth = CONTROL[me]
    score -= count.get(wealth, 0) * 0.4

    # 克我者
    officer = None
    for k, v in CONTROL.items():
        if v == me:
            officer = k
            break
    score -= count.get(officer, 0) * 0.7

    # 通根加分：日干在地支藏干中是否有同五行本气
    for pillar_hint in [month_zhi]:  # 月令通根最重要
        for hg, depth in CANG_GAN.get(pillar_hint, []):
            if GAN_WUXING[hg] == me and depth == "本气":
                score += 1.5
                break

    # 判定等级
    if score >= 8:
        level = "偏旺"
    elif score >= 5.5:
        level = "中和偏旺"
    elif score >= 3.5:
        level = "中和"
    elif score >= 2:
        level = "中和偏弱"
    else:
        level = "偏弱"

    return level, score, wx_state


def yongshen_advice(day_gan: str, strength: str) -> dict:
    """喜用神建议"""
    me = GAN_WUXING[day_gan]
    support = next((k for k, v in GENERATE.items() if v == me), None)
    output = GENERATE[me]
    wealth = CONTROL[me]
    officer = next((k for k, v in CONTROL.items() if v == me), None)

    if "旺" in strength:
        return {
            "倾向": "日主偏旺，宜泄耗克",
            "喜": [output, wealth, officer],
            "忌": [me, support],
        }
    elif "弱" in strength:
        return {
            "倾向": "日主偏弱，宜生扶",
            "喜": [me, support],
            "忌": [output, wealth, officer],
        }
    else:
        return {
            "倾向": "日主中和，以流通平衡为主",
            "喜": ["视格局而定"],
            "忌": ["过旺或过弱之五行"],
        }


def relation_analysis(pillars: list) -> list:
    """合冲刑害分析"""
    gans = [p[0] for p in pillars]
    zhis = [p[1] for p in pillars]
    results = []

    # 天干五合
    for i in range(len(gans)):
        for j in range(i + 1, len(gans)):
            pair = (gans[i], gans[j])
            pair_rev = (gans[j], gans[i])
            if pair in GAN_HE:
                results.append(f"天干五合：{gans[i]}{gans[j]}合{GAN_HE[pair]}")
            elif pair_rev in GAN_HE:
                results.append(f"天干五合：{gans[j]}{gans[i]}合{GAN_HE[pair_rev]}")

    # 地支关系
    for i in range(len(zhis)):
        for j in range(i + 1, len(zhis)):
            pair = (zhis[i], zhis[j])
            pair_rev = (zhis[j], zhis[i])

            if pair in ZHI_LIUHE:
                results.append(f"地支六合：{zhis[i]}{zhis[j]}合{ZHI_LIUHE[pair]}")
            elif pair_rev in ZHI_LIUHE:
                results.append(f"地支六合：{zhis[j]}{zhis[i]}合{ZHI_LIUHE[pair_rev]}")

            if pair in ZHI_CHONG or pair_rev in ZHI_CHONG:
                results.append(f"地支六冲：{zhis[i]}{zhis[j]}冲")

            if pair in ZHI_HAI or pair_rev in ZHI_HAI:
                results.append(f"地支六害：{zhis[i]}{zhis[j]}害")

    zhi_set = set(zhis)

    # 地支三合
    for combo, wx in ZHI_SANHE.items():
        if set(combo).issubset(zhi_set):
            results.append(f"地支三合：{''.join(combo)}合{wx}局")

    # 地支三会
    for combo, wx in ZHI_SANHUI.items():
        if set(combo).issubset(zhi_set):
            results.append(f"地支三会：{''.join(combo)}会{wx}局")

    # 三刑
    for combo in ZHI_XING_SAN:
        if set(combo).issubset(zhi_set):
            results.append(f"地支三刑：{''.join(combo)}刑")

    # 双刑（子卯）
    for combo in ZHI_XING_SHUANG:
        if combo[0] in zhi_set and combo[1] in zhi_set:
            results.append(f"地支相刑：{combo[0]}{combo[1]}刑")

    # 自刑（需同一地支出现两次及以上）
    for z in ZHI_XING_ZI:
        if zhis.count(z) >= 2:
            results.append(f"地支自刑：{z}{z}刑")

    return results


def changsheng_analysis(day_gan: str, pillars: list) -> list:
    """十二长生"""
    res = []
    for name, pillar in zip(["年柱", "月柱", "日柱", "时柱"], pillars):
        zhi = pillar[1]
        res.append(f"{name} {pillar}：{CHANGSHENG[day_gan][zhi]}")
    return res


def dayun_direction(year_gan: str, gender: str) -> str:
    """大运方向"""
    yy = GAN_YINYANG[year_gan]
    if gender == "male":
        return "顺行" if yy == "阳" else "逆行"
    else:
        return "顺行" if yy == "阴" else "逆行"


def dayun_list(month_pillar: str, direction: str, qiyun_age: float, count: int = 8) -> list:
    """大运列表（精确起运年龄）"""
    gan, zhi = split_pillar(month_pillar)
    gan_idx = GAN.index(gan)
    zhi_idx = ZHI.index(zhi)

    result = []
    for i in range(1, count + 1):
        if direction == "顺行":
            new_gan = GAN[(gan_idx + i) % 10]
            new_zhi = ZHI[(zhi_idx + i) % 12]
        else:
            new_gan = GAN[(gan_idx - i) % 10]
            new_zhi = ZHI[(zhi_idx - i) % 12]

        age1 = int(qiyun_age) + (i - 1) * 10
        age2 = age1 + 9
        result.append((f"{new_gan}{new_zhi}", age1, age2))

    return result


# ============================================================
# 神煞
# ============================================================

def get_taohua(day_zhi: str):
    m = {"申": "酉", "子": "酉", "辰": "酉",
         "寅": "卯", "午": "卯", "戌": "卯",
         "巳": "午", "酉": "午", "丑": "午",
         "亥": "子", "卯": "子", "未": "子"}
    return m.get(day_zhi)


def get_yima(day_zhi: str):
    m = {"申": "寅", "子": "寅", "辰": "寅",
         "寅": "申", "午": "申", "戌": "申",
         "巳": "亥", "酉": "亥", "丑": "亥",
         "亥": "巳", "卯": "巳", "未": "巳"}
    return m.get(day_zhi)


def get_huagai(day_zhi: str):
    m = {"申": "辰", "子": "辰", "辰": "辰",
         "寅": "戌", "午": "戌", "戌": "戌",
         "巳": "丑", "酉": "丑", "丑": "丑",
         "亥": "未", "卯": "未", "未": "未"}
    return m.get(day_zhi)


def get_wenchang(day_gan: str):
    return {"甲": "巳", "乙": "午", "丙": "申", "戊": "申",
            "丁": "酉", "己": "酉", "庚": "亥", "辛": "子",
            "壬": "寅", "癸": "卯"}.get(day_gan)


def get_tianyi(day_gan: str):
    return {"甲": ["丑", "未"], "戊": ["丑", "未"], "庚": ["丑", "未"],
            "乙": ["子", "申"], "己": ["子", "申"],
            "丙": ["亥", "酉"], "丁": ["亥", "酉"],
            "壬": ["卯", "巳"], "癸": ["卯", "巳"],
            "辛": ["寅", "午"]}.get(day_gan, [])


def shensha_analysis(day_gan: str, day_zhi: str, pillars: list) -> list:
    zhis = [p[1] for p in pillars]
    result = []
    taohua = get_taohua(day_zhi)
    yima = get_yima(day_zhi)
    huagai = get_huagai(day_zhi)
    wenchang = get_wenchang(day_gan)
    tianyi = get_tianyi(day_gan)

    if taohua and taohua in zhis:
        result.append(f"桃花：见{taohua}")
    if yima and yima in zhis:
        result.append(f"驿马：见{yima}")
    if huagai and huagai in zhis:
        result.append(f"华盖：见{huagai}")
    if wenchang and wenchang in zhis:
        result.append(f"文昌：见{wenchang}")
    for z in tianyi:
        if z in zhis:
            result.append(f"天乙贵人：见{z}")
    if not result:
        result.append("常见神煞未见明显触发")
    return result


# ============================================================
# 胎元、命宫
# ============================================================

def taiyuan(month_pillar: str) -> str:
    """胎元：月干进一位，月支进三位"""
    mg, mz = month_pillar[0], month_pillar[1]
    gan = GAN[(GAN.index(mg) + 1) % 10]
    zhi = ZHI[(ZHI.index(mz) + 3) % 12]
    return gan + zhi


def minggong(month_zhi: str, hour_zhi: str) -> str:
    """
    命宫（标准算法）：
    以子为正月（数到出生月），再以出生时逆数到卯。
    公式：命宫地支 = (14 - 月支数 - 时支数) mod 12
    其中：寅=1, 卯=2, ..., 丑=12
    """
    # 转换为 寅=1 的序数体系
    yin_order = {"寅": 1, "卯": 2, "辰": 3, "巳": 4, "午": 5, "未": 6,
                 "申": 7, "酉": 8, "戌": 9, "亥": 10, "子": 11, "丑": 12}
    m_num = yin_order[month_zhi]
    h_num = yin_order[hour_zhi]

    raw = 14 - m_num - h_num
    if raw <= 0:
        raw += 12

    # 转回 子=0 体系
    idx_to_zhi = {1: "寅", 2: "卯", 3: "辰", 4: "巳", 5: "午", 6: "未",
                  7: "申", 8: "酉", 9: "戌", 10: "亥", 11: "子", 12: "丑"}
    return idx_to_zhi[raw]


# ============================================================
# 空亡
# ============================================================

def get_kongwang(day_pillar: str):
    return KONGWANG.get(day_pillar, ("未知", "未知"))


# ============================================================
# 流年
# ============================================================

def ganzhi_by_year(year: int) -> str:
    offset = year - 1984
    return GAN[offset % 10] + ZHI[offset % 12]


def liunian_analysis(start_year: int, years: int, day_gan: str, pillars: list) -> list:
    natal_zhis = [p[1] for p in pillars]
    result = []
    for y in range(start_year, start_year + years):
        gz = ganzhi_by_year(y)
        gan, zhi = gz[0], gz[1]
        ss = get_shishen(day_gan, gan)
        events = []
        for nz in natal_zhis:
            pair = (zhi, nz)
            pair_rev = (nz, zhi)
            if pair in ZHI_CHONG or pair_rev in ZHI_CHONG:
                events.append(f"冲{nz}")
            if pair in ZHI_LIUHE or pair_rev in ZHI_LIUHE:
                events.append(f"合{nz}")
            if pair in ZHI_HAI or pair_rev in ZHI_HAI:
                events.append(f"害{nz}")
        result.append({
            "year": y, "ganzhi": gz, "shishen": ss, "events": events,
        })
    return result


# ============================================================
# 报告生成
# ============================================================

def build_report(dt: datetime, gender: str, time_unknown: bool = False):
    year_p = year_ganzhi(dt)
    year_gan, year_zhi = split_pillar(year_p)

    month_p = month_ganzhi(dt, year_gan)
    day_p = day_ganzhi(dt)
    day_gan, day_zhi = split_pillar(day_p)

    hour_p = hour_ganzhi(dt, day_gan)

    pillars = [year_p, month_p, day_p, hour_p]
    names = ["年柱", "月柱", "日柱", "时柱"]

    count = wuxing_count(pillars)
    strength, score, wx_state = day_master_strength(day_gan, month_p[1], count)
    yongshen = yongshen_advice(day_gan, strength)
    relations = relation_analysis(pillars)
    changsheng = changsheng_analysis(day_gan, pillars)

    direction = dayun_direction(year_gan, gender)
    qiyun_age = calc_qiyun_age(dt, year_gan, month_p, gender)
    dayuns = dayun_list(month_p, direction, qiyun_age)

    print("=" * 60)
    print("八字排盘结果（精确节气版）")
    print("=" * 60)
    print(f"出生时间：{dt}")
    print(f"性别：{'男' if gender == 'male' else '女'}")
    if time_unknown:
        print("[!] 未提供出生时间，默认按 00:00（子时）推算，时柱仅供参考！")
    print()

    print("四柱：")
    for n, p in zip(names, pillars):
        gan, zhi = split_pillar(p)
        cang_str = "、".join(f"{g}({d})" for g, d in CANG_GAN[zhi])
        print(
            f"  {n}：{p}  "
            f"天干五行={GAN_WUXING[gan]}({GAN_YINYANG[gan]})  "
            f"地支五行={ZHI_WUXING[zhi]}({ZHI_YINYANG[zhi]})  "
            f"藏干={cang_str}"
        )
    print()

    print("十神：")
    for n, p in zip(names, pillars):
        gan, zhi = split_pillar(p)
        gan_ss = "日主" if n == "日柱" else get_shishen(day_gan, gan)
        hidden_ss = [f"{h}({d}):{get_shishen(day_gan, h)}" for h, d in CANG_GAN[zhi]]
        print(f"  {n} {p}：天干={gan_ss}，藏干十神={hidden_ss}")
    print()

    print("五行统计：")
    for wx in ["木", "火", "土", "金", "水"]:
        print(f"  {wx}：{count[wx]:.1f}")
    print()

    print("日主强弱：")
    print(f"  日主：{day_gan}{GAN_WUXING[day_gan]}（{GAN_YINYANG[day_gan]}）")
    print(f"  月令状态：{wx_state}")
    print(f"  强弱：{strength}，评分：{score:.2f}")
    print()

    print("喜用神建议：")
    print(f"  倾向：{yongshen['倾向']}")
    print(f"  喜：{yongshen['喜']}")
    print(f"  忌：{yongshen['忌']}")
    print()

    print("合冲刑害：")
    if relations:
        for r in relations:
            print(f"  {r}")
    else:
        print("  未见明显合冲刑害")
    print()

    print("十二长生：")
    for item in changsheng:
        print(f"  {item}")
    print()

    print("大运：")
    print(f"  大运方向：{direction}")
    print(f"  起运年龄：{qiyun_age:.1f} 岁")
    for p, a1, a2 in dayuns:
        print(f"  {a1:02d}–{a2:02d}岁：{p}")
    print()

    print("纳音：")
    for n, p in zip(names, pillars):
        print(f"  {n} {p}：{NAYIN.get(p, '未知')}")
    print()

    print("空亡：")
    kw = get_kongwang(day_p)
    print(f"  日柱 {day_p} 空亡：{kw[0]}、{kw[1]}")
    print()

    print("神煞：")
    shensha = shensha_analysis(day_gan, day_zhi, pillars)
    for s in shensha:
        print(f"  {s}")
    print()

    print("胎元 / 命宫：")
    ty = taiyuan(month_p)
    mg = minggong(month_p[1], hour_p[1])
    print(f"  胎元：{ty}，纳音：{NAYIN.get(ty, '未知')}")
    print(f"  命宫：{mg}")
    print()

    print("未来 10 年流年：")
    current_year = datetime.now().year
    liunians = liunian_analysis(current_year, 10, day_gan, pillars)
    for item in liunians:
        ev = "，".join(item["events"]) if item["events"] else "无明显冲合害"
        print(f"  {item['year']}年 {item['ganzhi']}：十神={item['shishen']}，关系={ev}")
    print()

    print("简易分析：")
    print(make_simple_text(day_gan, count, strength, yongshen, relations, wx_state))


def make_simple_text(day_gan: str, count: dict, strength: str,
                     yongshen: dict, relations: list, wx_state: str) -> str:
    me = GAN_WUXING[day_gan]
    strongest = max(count, key=count.get)
    weakest = min(count, key=count.get)

    text = []
    text.append(f"此命以{day_gan}{me}为日主，月令{me}处「{wx_state}」地。")
    text.append(f"五行中{strongest}较明显，{weakest}较弱。")
    text.append("五行偏多者，往往代表该类气势、环境或行为模式较突出；"
                "偏少者，则代表该类资源、性格倾向或外部条件较不足。")
    text.append(f"日主强弱判断为：{strength}。")

    if "旺" in strength:
        text.append("日主偏旺，一般不宜继续过度生扶，宜通过泄秀、耗身、克制来取得平衡。")
    elif "弱" in strength:
        text.append("日主偏弱，一般宜印比生扶，不宜再被过度克泄耗。")
    else:
        text.append("日主中和，重点在于格局是否清纯、五行是否流通。")

    text.append(f"喜用倾向：{yongshen['倾向']}。")
    text.append(f"参考喜神：{yongshen['喜']}。")
    text.append(f"参考忌神：{yongshen['忌']}。")

    if relations:
        text.append("命局中存在合冲刑害，说明结构中有互动和变化，"
                    "具体吉凶需要结合位置、力量和岁运引动来看。")
    else:
        text.append("命局合冲刑害较少，结构相对平稳，但仍需结合大运流年判断变化。")

    text.append("神煞、纳音、命宫等可作辅助参考，不宜单独定吉凶。")
    text.append("此分析为传统命理规则推演，不应作为现实决策的唯一依据。")

    return "\n".join(text)


# ============================================================
# 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="传统八字排盘脚本（精确节气版）")
    parser.add_argument("--date", required=True, help="出生日期，例如 1998-08-15")
    parser.add_argument("--time", default=None,
                        help="出生时间，例如 14:30（不传则默认 00:00 子时，时柱仅供参考）")
    parser.add_argument("--gender", required=True, choices=["male", "female"],
                        help="性别 male/female")

    args = parser.parse_args()
    time_unknown = args.time is None
    time_str = args.time if args.time else "00:00"
    dt = datetime.strptime(args.date + " " + time_str, "%Y-%m-%d %H:%M")
    build_report(dt, args.gender, time_unknown=time_unknown)


if __name__ == "__main__":
    main()
