import unittest
import sys
from pathlib import Path

import pandas as pd
import sqlite3
sys.path.insert(1, str(Path(__file__).parents[1]))


from assignment import ex19 as ex


class TestMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn_orders = sqlite3.connect("orders.db")

               
    def test_1(self):
        sql_statement = ex()
        data = pd.read_csv("ex19.csv")        
        df = pd.read_sql_query(sql_statement, self.conn_orders)
        self.assertEqual(df.equals(data), True)

    @classmethod
    def tearDownClass(cls):
      cls.conn_orders.close()
  
if __name__ == '__main__':
    unittest.main()
