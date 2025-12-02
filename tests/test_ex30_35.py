import unittest
import sys
from pathlib import Path

import pandas as pd
import sqlite3
sys.path.insert(1, str(Path(__file__).parents[1]))


import assignment



class TestMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assignment.normalize_database('non_normalized.db')
        cls.conn_normalized = sqlite3.connect("normalized.db")
               
    def test_1(self):
        sql_statement = assignment.ex30(self.conn_normalized)
        df = pd.read_sql_query(sql_statement, self.conn_normalized)
        data = pd.read_csv("ex30.csv")
        self.assertEqual(df.equals(data), True)

    def test_2(self):
        sql_statement = assignment.ex31(self.conn_normalized)
        df = pd.read_sql_query(sql_statement, self.conn_normalized)
        data = pd.read_csv("ex31.csv")
        self.assertEqual(df.equals(data), True)

    def test_3(self):
        sql_statement = assignment.ex32(self.conn_normalized)
        df = pd.read_sql_query(sql_statement, self.conn_normalized)
        data = pd.read_csv("ex32.csv")
        self.assertEqual(df.equals(data), True)
    
    def test_4(self):
        sql_statement = assignment.ex33(self.conn_normalized)
        df = pd.read_sql_query(sql_statement, self.conn_normalized)
        data = pd.read_csv("ex33.csv")
        self.assertEqual(df.equals(data), True)

    def test_5(self):
        sql_statement = assignment.ex34(self.conn_normalized)
        df = pd.read_sql_query(sql_statement, self.conn_normalized)
        data = pd.read_csv("ex34.csv")
        self.assertEqual(df.equals(data), True)

    def test_6(self):
        sql_statement = assignment.ex35(self.conn_normalized)
        df = pd.read_sql_query(sql_statement, self.conn_normalized)
        data = pd.read_csv("ex35.csv")
        self.assertEqual(df.equals(data), True)

    @classmethod
    def tearDownClass(cls):
      cls.conn_normalized.close()
  
if __name__ == '__main__':
    unittest.main()
