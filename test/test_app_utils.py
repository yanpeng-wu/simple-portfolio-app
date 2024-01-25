
import unittest
import pandas as pd
from src import app_utils

class TestAppUtils(unittest.TestCase):

    def test_max_drawdown(self):
        return_ts = pd.Series([0.0500, -0.0952, 0.1579, -0.1091, -0.0102, 0.0722, -0.0192])
        max_dd = app_utils.max_drawdown(return_ts)
        expected = -0.118187
        self.assertAlmostEqual(max_dd, expected, places=6)

if __name__ == '__main__':
    unittest.main()