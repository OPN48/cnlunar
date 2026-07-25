import datetime
import unittest

import cnlunar


class GreatSmallWasteTest(unittest.TestCase):
    # 《钦定协纪辨方书》卷四将破日称为大耗；以下覆盖子至亥十二个月建。
    great_waste_cases = [
        ((2024, 12, 8), '子', '丙午'),
        ((2024, 1, 8), '丑', '辛未'),
        ((2024, 2, 14), '寅', '戊申'),
        ((2024, 3, 10), '卯', '癸酉'),
        ((2024, 4, 4), '辰', '戊戌'),
        ((2024, 5, 11), '巳', '乙亥'),
        ((2024, 6, 5), '午', '庚子'),
        ((2024, 7, 12), '未', '丁丑'),
        ((2024, 8, 18), '申', '甲寅'),
        ((2024, 9, 12), '酉', '己卯'),
        ((2024, 10, 19), '戌', '丙辰'),
        ((2024, 11, 13), '亥', '辛巳'),
    ]

    # 卷四称“执……又为小耗”；以下覆盖子至亥十二个月建。
    small_waste_cases = [
        ((2024, 12, 7), '子', '乙巳'),
        ((2024, 1, 7), '丑', '庚午'),
        ((2024, 2, 13), '寅', '丁未'),
        ((2024, 3, 9), '卯', '壬申'),
        ((2024, 4, 15), '辰', '己酉'),
        ((2024, 5, 10), '巳', '甲戌'),
        ((2024, 6, 16), '午', '辛亥'),
        ((2024, 7, 11), '未', '丙子'),
        ((2024, 8, 17), '申', '癸丑'),
        ((2024, 9, 11), '酉', '戊寅'),
        ((2024, 10, 18), '戌', '乙卯'),
        ((2024, 11, 12), '亥', '庚辰'),
    ]

    @staticmethod
    def lunar(date_tuple, god_type='8char'):
        return cnlunar.Lunar(
            datetime.datetime(*date_tuple, 12, 0),
            godType=god_type,
        )

    def test_great_waste_matches_month_break_for_all_months(self):
        for date_tuple, month_branch, day_ganzhi in self.great_waste_cases:
            with self.subTest(date=date_tuple):
                lunar = self.lunar(date_tuple)
                self.assertEqual(lunar.month8Char[1], month_branch)
                self.assertEqual(lunar.day8Char, day_ganzhi)
                self.assertEqual(lunar.today12DayOfficer, '破')
                self.assertIn('月破', lunar.badGodName)
                self.assertIn('大耗', lunar.badGodName)

    def test_small_waste_matches_officer_day_for_all_months(self):
        for date_tuple, month_branch, day_ganzhi in self.small_waste_cases:
            with self.subTest(date=date_tuple):
                lunar = self.lunar(date_tuple)
                self.assertEqual(lunar.month8Char[1], month_branch)
                self.assertEqual(lunar.day8Char, day_ganzhi)
                self.assertEqual(lunar.today12DayOfficer, '执')
                self.assertIn('小耗', lunar.badGodName)

    def test_old_shifted_tables_no_longer_match(self):
        cases = [
            ((2026, 2, 13), '寅', '戊午', '定', '大耗'),
            ((2026, 1, 6), '丑', '庚辰', '平', '小耗'),
        ]

        for date_tuple, month_branch, day_ganzhi, officer, deity in cases:
            with self.subTest(date=date_tuple, deity=deity):
                lunar = self.lunar(date_tuple)
                self.assertEqual(lunar.month8Char[1], month_branch)
                self.assertEqual(lunar.day8Char, day_ganzhi)
                self.assertEqual(lunar.today12DayOfficer, officer)
                self.assertNotIn(deity, lunar.badGodName)

    def test_corrected_representative_dates_match(self):
        cases = [
            ((2026, 2, 15), '寅', '庚申', '破', ('月破', '大耗')),
            ((2026, 1, 8), '丑', '壬午', '执', ('小耗',)),
        ]

        for date_tuple, month_branch, day_ganzhi, officer, deities in cases:
            with self.subTest(date=date_tuple):
                lunar = self.lunar(date_tuple)
                self.assertEqual(lunar.month8Char[1], month_branch)
                self.assertEqual(lunar.day8Char, day_ganzhi)
                self.assertEqual(lunar.today12DayOfficer, officer)
                for deity in deities:
                    self.assertIn(deity, lunar.badGodName)


if __name__ == '__main__':
    unittest.main()
