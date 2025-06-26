import unittest
from datetime import datetime
from app import is_date

class TestDateValidator(unittest.TestCase):
    def test_valid_dates(self):
        test_cases = [
            ("01.01.2023", "2023-01-01"),
            ("31.12.2023", "2023-12-31"),
            ("28.02.2023", "2023-02-28"),
            ("29.02.2024", "2024-02-29"),
            ("2023-05-15", "2023-05-15"),
            ("2024-02-29", "2024-02-29")
        ]

        for input_date, expected_output in test_cases:
            with self.subTest(input_date=input_date):
                result = is_date(input_date)
                self.assertEqual(result, expected_output)

    def test_invalid_dates(self):
        invalid_dates = [
            "32.01.2023",  # Несуществующий день
            "00.01.2023",  # Нулевой день
            "15.13.2023",  # Несуществующий месяц
            "15.00.2023",  # Нулевой месяц
            "2023-02-30",  # Несуществующий день (февраль)
            "2023-13-01",  # Несуществующий месяц
            "29.02.2023",  # Не високосный год
            "01/01/2023",  # Неправильный разделитель
            "2023_05_15",  # Неправильный разделитель
            "abcd",        # Мусор
            "",            # Пустая строка
            "15.05.23",    # Двухзначный год
            "2023-5-15",   # Месяц без ведущего нуля
            "15.5.2023"    # Месяц без ведущего нуля
        ]

        for date_str in invalid_dates:
            with self.subTest(date_str=date_str):
                self.assertFalse(is_date(date_str))

    def test_edge_cases(self):
        edge_cases = [
            ("01.01.0001", "0001-01-01"),  # Минимальная дата
            ("31.12.9999", "9999-12-31"),  # Максимальная дата
            (" 01.01.2023 ", "2023-01-01"),  # Пробелы
            ("01.01.2023\n", "2023-01-01")   # Символы переноса
        ]

        for input_date, expected_output in edge_cases:
            with self.subTest(input_date=input_date):
                result = is_date(input_date.strip())
                self.assertEqual(result, expected_output)

    def test_format_handling(self):
        self.assertEqual(is_date("01.01.2023"), "2023-01-01")
        self.assertEqual(is_date("2023-01-01"), "2023-01-01")
        self.assertNotEqual(is_date("01.01.2023"), "01.01.2023")  # Проверка нормализации

    def test_leap_years(self):
        self.assertEqual(is_date("29.02.2020"), "2020-02-29")
        self.assertEqual(is_date("29.02.2000"), "2000-02-29")
        self.assertFalse(is_date("29.02.2023"))
        self.assertFalse(is_date("29.02.1900"))  # 1900 не високосный

if __name__ == '__main__':
    unittest.main()