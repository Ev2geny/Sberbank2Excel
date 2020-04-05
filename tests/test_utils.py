from unittest import TestCase



class Test(TestCase):
    def test_get_period_balance(self):
        from core.utils import get_period_balance
        my_str = '1 290 600,06 ₽                               +  СУММА ПОПОЛНЕНИЙ                         1 455 130,00    – СУММА СПИСАНИЙ                               65 529,94 '
        self.assertAlmostEqual(get_period_balance(my_str), 1389600.06)

        my_str = '1 290 700,06 ₽                               +  СУММА ПОПОЛНЕНИЙ                         1 455 131,00    – СУММА СПИСАНИЙ                               65 529,95 '
        self.assertAlmostEqual(get_period_balance(my_str), 1389601.05)

