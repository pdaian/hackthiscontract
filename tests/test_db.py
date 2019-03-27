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
        self.MOCK_USER = "0x2AA1710B555E6cc1Ac98c0eC48B51d61f3273949"
        self.MOCK_CONTRACT_ADDRESS = "0x0000000000000000000000000000000000000018"
        self.VALID_ADDRESSES = ["0x0000000000000000000000000000000000000008",
                                "0x31b98d14007bdee637298086988a0bbd31184523",
                                "0xFFe7642922f0F6010291acd934bb18F174aaa218",
                                "0xEAf21008167fb3cC43a82B6197C273a7424322C8",
                                "0xc0fcd7514CBfC90A36E4bB21AD49845A4c3b3D54",
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
        c1finished INTEGER,
        c2state INTEGER,
        c2deployaddr TEXT,
        c2finished INTEGER,
        c3state INTEGER,
        c3deployaddr TEXT,
        c3finished INTEGER,
        c4state INTEGER,
        c4deployaddr TEXT,
        c4finished INTEGER,
        c5state INTEGER,
        c5deployaddr TEXT,
        c5finished INTEGER
    )"""
            self.assertEqual(list(resp)[0][0], expected_create_string)

    def test_exists(self):
        with run.app.app_context():
            self.assertFalse(util.exists(self.VALID_ADDRESSES[1]))
            conn = sqlite3.connect(constants.DB_PATH)
            cur = conn.cursor()
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            self.assertTupleEqual(val,
                    (
                        1, #userid
                        self.VALID_ADDRESSES[1], #useraddress
                        0, # score
                        0, # c1state
                        None, # c1deployaddr
                        0, # c1finished
                        0, #c2state
                        None, # c2deployaddr
                        0, # c2finished
                        0, #c3state
                        None, # c3deployaddr
                        0, # c3finished
                        0, #c4state
                        None, # c4deployaddr
                        0, # c4finished
                        0, # c5state
                        None, # c5deployaddr
                        0 # c5finished
                    ))

            conn.close()
            self.assertTrue(util.exists(self.VALID_ADDRESSES[1]))

    def test_write_address(self):
        with run.app.app_context():
            util.write_address(self.MOCK_USER, 1, self.MOCK_CONTRACT_ADDRESS)
            conn = sqlite3.connect(constants.DB_PATH)
            cur = conn.cursor()
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            self.assertTupleEqual(val,
                    (
                        1, #userid
                        self.MOCK_USER, #useraddress
                        0, # score
                        1, # c1state
                        self.MOCK_CONTRACT_ADDRESS, # c1deployaddr
                        0, # c1finished
                        0, #c2state
                        None, # c2deployaddr
                        0, # c2finished
                        0, #c3state
                        None, # c3deployaddr
                        0, # c3finished
                        0, #c4state
                        None, # c4deployaddr
                        0, # c4finished
                        0, # c5state
                        None, # c5deployaddr
                        0 # c5finished
                    ))
            conn.close()

    def test_erase_challenge_deployed_address_from_db(self):
        with run.app.app_context():
            util.write_address(self.MOCK_USER, 1, self.MOCK_CONTRACT_ADDRESS)
            util.erase_challenge_deployed_address_from_db(self.MOCK_USER, 1)
            conn = sqlite3.connect(constants.DB_PATH)
            cur = conn.cursor()
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            self.assertTupleEqual(val,
                    (
                        1, #userid
                        self.MOCK_USER, #useraddress
                        0, # score
                        0, # c1state
                        None, # c1deployaddr
                        0, # c1finished
                        0, #c2state
                        None, # c2deployaddr
                        0, # c2finished
                        0, #c3state
                        None, # c3deployaddr
                        0, # c3finished
                        0, #c4state
                        None, # c4deployaddr
                        0, # c4finished
                        0, # c5state
                        None, # c5deployaddr
                        0 # c5finished
                    ))
            conn.close()

    def test_get_deployed_contract_address_for_challenge(self):
        with run.app.app_context():
            util.write_address(self.MOCK_USER, 1, self.MOCK_CONTRACT_ADDRESS)
            self.assertEqual(self.MOCK_CONTRACT_ADDRESS, util.get_deployed_contract_address_for_challenge(self.MOCK_USER, 1))

    def test_mark_in_progress(self):
        with run.app.app_context():
            util.write_address(self.MOCK_USER, 1, self.MOCK_CONTRACT_ADDRESS)
            util.mark_finished(self.MOCK_USER, "01_naive_programmer")
            util.mark_in_progress(self.MOCK_USER, 1)
            conn = sqlite3.connect(constants.DB_PATH)
            cur = conn.cursor()
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            #                         userid   useraddress score c1state c1depoyaddr            c2state c2deployaddr c3state c3deployaddr c4state c4deployaddr
            self.assertTupleEqual(val,
                (
                    1, # userid
                    self.MOCK_USER, # useraddress
                    1, # score
                    1, # c1state
                    self.MOCK_CONTRACT_ADDRESS, # c1deployaddr
                    1, # c1finished
                    0, # c2state
                    None, # c2deployaddr
                    0, # c2finished
                    0, # c3state
                    None, #c3deployaddr
                    0, # c3finished
                    0, # c4state
                    None, # c4deployaddr
                    0, # c4finished
                    0, # c5state
                    None, # c5deployaddr
                    0 #c5finished
                )
            )
            conn.close()


    def test_malicious_mark_finished(self):
        with run.app.app_context():
            conn = sqlite3.connect(constants.DB_PATH)
            cur = conn.cursor()
            util.write_address(self.MOCK_USER, 1, self.MOCK_CONTRACT_ADDRESS)
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            self.assertTupleEqual(val,
                (
                    1, # userid
                    self.MOCK_USER, # useraddress
                    0, # score
                    constants.STATE_DEPLOYED_IN_PROGRESS, # c1state
                    self.MOCK_CONTRACT_ADDRESS, # c1deployaddr
                    0, # c1finished
                    0, # c2state
                    None, # c2deployaddr
                    0, # c2finished
                    0, # c3state
                    None, #c3deployaddr
                    0, # c3finished
                    0, # c4state
                    None, # c4deployaddr
                    0, # c4finished
                    0, # c5state
                    None, # c5deployaddr
                    0 #c5finished
                )
            )

            util.mark_in_progress(self.MOCK_USER, 1)
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            self.assertTupleEqual(val,
                (
                    1, # userid
                    self.MOCK_USER, # useraddress
                    0, # score
                    constants.STATE_DEPLOYED_IN_PROGRESS, # c1state
                    self.MOCK_CONTRACT_ADDRESS, # c1deployaddr
                    0, # c1finished
                    0, # c2state
                    None, # c2deployaddr
                    0, # c2finished
                    0, # c3state
                    None, #c3deployaddr
                    0, # c3finished
                    0, # c4state
                    None, # c4deployaddr
                    0, # c4finished
                    0, # c5state
                    None, # c5deployaddr
                    0 #c5finished
                )
            )

            util.mark_finished(self.MOCK_USER, "01_naive_programmer")
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            self.assertTupleEqual(val,
                (
                    1, # userid
                    self.MOCK_USER, # useraddress
                    1, # score
                    constants.STATE_FINISHED, # c1state
                    self.MOCK_CONTRACT_ADDRESS, # c1deployaddr
                    1, # c1finished
                    0, # c2state
                    None, # c2deployaddr
                    0, # c2finished
                    0, # c3state
                    None, #c3deployaddr
                    0, # c3finished
                    0, # c4state
                    None, # c4deployaddr
                    0, # c4finished
                    0, # c5state
                    None, # c5deployaddr
                    0 #c5finished
                )
            )

            util.mark_finished(self.MOCK_USER, "01_naive_programmer")
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            self.assertTupleEqual(val,
                (
                    1, # userid
                    self.MOCK_USER, # useraddress
                    1, # score
                    constants.STATE_FINISHED, # c1state
                    self.MOCK_CONTRACT_ADDRESS, # c1deployaddr
                    1, # c1finished
                    0, # c2state
                    None, # c2deployaddr
                    0, # c2finished
                    0, # c3state
                    None, #c3deployaddr
                    0, # c3finished
                    0, # c4state
                    None, # c4deployaddr
                    0, # c4finished
                    0, # c5state
                    None, # c5deployaddr
                    0 #c5finished
                )
            )

            util.write_address(self.MOCK_USER, 1, self.VALID_ADDRESSES[1])
            util.mark_in_progress(self.MOCK_USER, 1)
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            self.assertTupleEqual(val,
                (
                    1, # userid
                    self.MOCK_USER, # useraddress
                    1, # score
                    constants.STATE_DEPLOYED_IN_PROGRESS, # c1state
                    self.VALID_ADDRESSES[1], # c1deployaddr
                    1, # c1finished
                    0, # c2state
                    None, # c2deployaddr
                    0, # c2finished
                    0, # c3state
                    None, #c3deployaddr
                    0, # c3finished
                    0, # c4state
                    None, # c4deployaddr
                    0, # c4finished
                    0, # c5state
                    None, # c5deployaddr
                    0 #c5finished
                )
            )

            util.mark_grading(self.MOCK_USER, 1)
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            self.assertTupleEqual(val,
                (
                    1, # userid
                    self.MOCK_USER, # useraddress
                    1, # score
                    constants.STATE_GRADING, # c1state
                    self.VALID_ADDRESSES[1], # c1deployaddr
                    1, # c1finished
                    0, # c2state
                    None, # c2deployaddr
                    0, # c2finished
                    0, # c3state
                    None, #c3deployaddr
                    0, # c3finished
                    0, # c4state
                    None, # c4deployaddr
                    0, # c4finished
                    0, # c5state
                    None, # c5deployaddr
                    0 #c5finished
                )
            )
            util.mark_finished(self.MOCK_USER, "01_naive_programmer")
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            self.assertTupleEqual(val,
                (
                    1, # userid
                    self.MOCK_USER, # useraddress
                    1, # score
                    constants.STATE_FINISHED, # c1state
                    self.VALID_ADDRESSES[1], # c1deployaddr
                    1, # c1finished
                    0, # c2state
                    None, # c2deployaddr
                    0, # c2finished
                    0, # c3state
                    None, #c3deployaddr
                    0, # c3finished
                    0, # c4state
                    None, # c4deployaddr
                    0, # c4finished
                    0, # c5state
                    None, # c5deployaddr
                    0 #c5finished
                )
            )

            conn.close()


    def test_mark_grading(self):
        with run.app.app_context():
            util.write_address(self.MOCK_USER, 1, self.MOCK_CONTRACT_ADDRESS)
            util.mark_grading(self.MOCK_USER, 1)
            conn = sqlite3.connect(constants.DB_PATH)
            cur = conn.cursor()
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            self.assertTupleEqual(val,
                    (
                        1, #userid
                        self.MOCK_USER, #useraddress
                        0, # score
                        3, # c1state
                        self.MOCK_CONTRACT_ADDRESS, # c1deployaddr
                        0, #c1finished
                        0, #c2state
                        None, # c2deployaddr
                        0, #c2finished
                        0, #c3state
                        None, # c3deployaddr
                        0, #c3finished
                        0, #c4state
                        None, # c4deployaddr
                        0, #c4finished
                        0, # c5state
                        None, # c4deployaddr
                        0 #c5finished
                    ))
            conn.close()

    def test_mark_finished(self):
        with run.app.app_context():
            util.write_address(self.MOCK_USER, 1, self.MOCK_CONTRACT_ADDRESS)
            util.mark_finished(self.MOCK_USER, "01_naive_programmer")
            conn = sqlite3.connect(constants.DB_PATH)
            cur = conn.cursor()
            resp = cur.execute("SELECT * FROM htctable")
            val = list(resp)[0]
            self.assertTupleEqual(val,
                    (
                        1, #userid
                        self.MOCK_USER, #useraddress
                        1, # score
                        2, # c1state
                        self.MOCK_CONTRACT_ADDRESS, # c1deployaddr
                        1, #c1finished
                        0, #c2state
                        None, # c2deployaddr
                        0, #c2finished
                        0, #c3state
                        None, # c3deployaddr
                        0, #c3finished
                        0, #c4state
                        None, # c4deployaddr
                        0, #c4finished
                        0, # c5state
                        None, # c4deployaddr
                        0 #c5finished
                    ))

            conn.close()

    def test_get_status(self):
        ns = ("Not Started", "red")
        dep = ("Deployed / Unfinished", "black", self.MOCK_CONTRACT_ADDRESS)
        fin = ("Done!", "green", self.MOCK_CONTRACT_ADDRESS)
        with run.app.app_context():
            stat = util.get_status(self.MOCK_USER, 1)
            self.assertTupleEqual(stat, ns)
            util.exists(self.MOCK_USER)
            stat = util.get_status(self.MOCK_USER, 1)
            self.assertTupleEqual(stat, ns)
            util.write_address(self.MOCK_USER, 1, self.MOCK_CONTRACT_ADDRESS)
            stat = util.get_status(self.MOCK_USER, 1)
            self.assertTupleEqual(stat, dep)
            util.mark_finished(self.MOCK_USER, "01_naive_programmer")
            stat = util.get_status(self.MOCK_USER, 1)
            self.assertTupleEqual(stat, fin)

    def test_get_ranking_from_db(self):
        with run.app.app_context():
            util.write_address(self.MOCK_USER, 1, self.MOCK_CONTRACT_ADDRESS)
            util.mark_finished(self.MOCK_USER, "01_naive_programmer")

            util.write_address(self.VALID_ADDRESSES[0], 2, self.VALID_ADDRESSES[1])
            util.mark_finished(self.VALID_ADDRESSES[0], "02_coinflip")

            util.write_address(self.VALID_ADDRESSES[0], 3, self.VALID_ADDRESSES[2])
            util.mark_finished(self.VALID_ADDRESSES[0], "03_ERC20")

            util.write_address(self.VALID_ADDRESSES[3], 5, self.VALID_ADDRESSES[4])
            util.mark_finished(self.VALID_ADDRESSES[3], "05_bad_ico")

            ranking = util.get_ranking_from_db()
            self.assertListEqual(
                    [
                        (self.VALID_ADDRESSES[0], 6),
                        (self.VALID_ADDRESSES[3], 3),
                        (self.MOCK_USER, 1),
                    ],
                    ranking)

if __name__ == '__main__':
    unittest.main()
