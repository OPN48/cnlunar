import datetime
import unittest

import cnlunar


class HeavenlyWishTest(unittest.TestCase):
    # 《钦定协纪辨方书》卷五校正表的十二个月命中样本。
    corrected_cases = [
        ((2024, 12, 15), '子', '癸丑'),
        ((2030, 1, 29), '丑', '甲子'),
        ((2026, 3, 2), '寅', '乙亥'),
        ((2024, 3, 11), '卯', '甲戌'),
        ((2028, 4, 30), '辰', '乙酉'),
        ((2024, 6, 1), '巳', '丙申'),
        ((2024, 6, 12), '午', '丁未'),
        ((2027, 8, 7), '未', '戊午'),
        ((2024, 9, 2), '申', '己巳'),
        ((2024, 9, 13), '酉', '庚辰'),
        ((2028, 11, 2), '戌', '辛卯'),
        ((2024, 12, 4), '亥', '壬寅'),
    ]

    # 旧《历例》表独有的命中样本；卷五校正后均不应命中。
    rejected_old_table_cases = [
        ((2024, 1, 1), '子', '甲子'),
        ((2024, 1, 20), '丑', '癸未'),
        ((2030, 2, 28), '寅', '甲午'),
        ((2024, 5, 12), '巳', '丙子'),
        ((2026, 7, 2), '午', '丁丑'),
        ((2024, 8, 18), '申', '甲寅'),
        ((2027, 10, 4), '酉', '丙辰'),
        ((2029, 12, 4), '亥', '戊辰'),
    ]

    @staticmethod
    def lunar(date_tuple):
        return cnlunar.Lunar(
            datetime.datetime(*date_tuple, 12, 0),
            godType='8char',
        )

    def test_corrected_table_matches_all_months(self):
        for date_tuple, month_branch, day_ganzhi in self.corrected_cases:
            with self.subTest(date=date_tuple):
                lunar = self.lunar(date_tuple)
                self.assertEqual(lunar.month8Char[1], month_branch)
                self.assertEqual(lunar.day8Char, day_ganzhi)
                self.assertIn('天愿', lunar.goodGodName)

    def test_rejected_old_table_does_not_match(self):
        for date_tuple, month_branch, day_ganzhi in self.rejected_old_table_cases:
            with self.subTest(date=date_tuple):
                lunar = self.lunar(date_tuple)
                self.assertEqual(lunar.month8Char[1], month_branch)
                self.assertEqual(lunar.day8Char, day_ganzhi)
                self.assertNotIn('天愿', lunar.goodGodName)


if __name__ == '__main__':
    unittest.main()
