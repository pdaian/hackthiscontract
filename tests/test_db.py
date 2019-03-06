import os
import unittest
import sys
import sqlite3

sys.path.insert(0, os.path.abspath('.'))
import config as constants
import util
import run


class HackThisContractDBTest(unittest.TestCase):
    def setUp(self):
        self.app = run.app.test_client()
        self.MOCK_USER = "0x0000000000000000000000000000000000000008"
        self.MOCK_CONTRACT_ADDRESS = "0x0000000000000000000000000000000000000018"
        self.VALID_ADDRESSES = ["0x0000000000000000000000000000000000000008",
                                "0x31b98d14007bdee637298086988a0bbd31184523",
                                "0xb279182d99e65703f0076e4812653aab85fca0f0"]
        self.VALID_CHALLENGE = "03_ERC20"
        with run.app.app_context():
            util.init_db()

    def tearDown(self):
        if os.path.isfile(constants.DB_PATH):
            os.remove(constants.DB_PATH)

    def test_index_loads(self):
        result = self.app.get("/")
        self.assertIsNotNone(result.data)

    def test_init_db(self):
        with run.app.app_context():
            self.assertTrue(os.path.isfile(constants.DB_PATH))
            conn = sqlite3.connect(constants.DB_PATH)
            cur = conn.cursor()
            resp = cur.execute("SELECT sql FROM sqlite_master WHERE name = 'htctable'")
            self.assertTrue(resp)
            expected_create_string = """CREATE TABLE htctable(
        userid INTEGER PRIMARY KEY,
        useraddress TEXT NOT NULL UNIQUE,
        score INTEGER,
        c1state INTEGER,
        c1deployaddr TEXT,
        c2state INTEGER,
        c2deployaddr TEXT,
        c3state INTEGER,
        c3deployaddr TEXT,
        c4state INTEGER,
        c4deployaddr TEXT
    )"""
            self.assertEqual(list(resp)[0][0], expected_create_string)

    def test_exists(self):
        with run.app.app_context():
            self.assertFalse(util.exists(self.VALID_ADDRESSES[1]))
            conn = sqlite3.connect(constants.DB_PATH)
            cur = conn.cursor()
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            #                         userid   useraddress       score c1state c1depoyaddr c2state c2deployaddr c3state c3deployaddr c4state c4deployaddr
            self.assertTupleEqual(val, (1, self.VALID_ADDRESSES[1], 0,    0,    None,        0,      None,        0,      None,       0,       None))
            conn.close()
            self.assertTrue(util.exists(self.VALID_ADDRESSES[1]))

    def test_write_address(self):
        with run.app.app_context():
            util.write_address(self.MOCK_USER, 1, self.MOCK_CONTRACT_ADDRESS)
            conn = sqlite3.connect(constants.DB_PATH)
            cur = conn.cursor()
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            #                         userid   useraddress score c1state c1depoyaddr            c2state c2deployaddr c3state c3deployaddr c4state c4deployaddr
            self.assertTupleEqual(val, (1, self.MOCK_USER, 0,    1,    self.MOCK_CONTRACT_ADDRESS, 0,      None,        0,      None,       0,       None))
            conn.close()

    def test_mark_finished(self):
        with run.app.app_context():
            util.write_address(self.MOCK_USER, 1, self.MOCK_CONTRACT_ADDRESS)
            util.mark_finished(self.MOCK_USER, 1)
            conn = sqlite3.connect(constants.DB_PATH)
            cur = conn.cursor()
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            #                         userid   useraddress score c1state c1depoyaddr            c2state c2deployaddr c3state c3deployaddr c4state c4deployaddr
            self.assertTupleEqual(val, (1, self.MOCK_USER, 0,    2,    self.MOCK_CONTRACT_ADDRESS, 0,      None,        0,      None,       0,       None))
            conn.close()

    def test_get_status(self):
        nse = ("Not Started/Error", "red")
        ns = ("Not Started", "red")
        dep = ("Deployed / Unfinished", "black", self.MOCK_CONTRACT_ADDRESS)
        fin = ("Done!", "green", self.MOCK_CONTRACT_ADDRESS)
        with run.app.app_context():
            stat = util.get_status(self.MOCK_USER, 1)
            self.assertTupleEqual(stat, nse)
            util.exists(self.MOCK_USER)
            stat = util.get_status(self.MOCK_USER, 1)
            self.assertTupleEqual(stat, ns)
            util.write_address(self.MOCK_USER, 1, self.MOCK_CONTRACT_ADDRESS)
            stat = util.get_status(self.MOCK_USER, 1)
            self.assertTupleEqual(stat, dep)
            util.mark_finished(self.MOCK_USER, 1)
            stat = util.get_status(self.MOCK_USER, 1)
            self.assertTupleEqual(stat, fin)



if __name__ == '__main__':
    unittest.main()
