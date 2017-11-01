"""
@author twsswt
"""
import unittest

from mock import Mock

from random import Random

from ecounting_workflow.ecount_system import Ballot, BallotScanner, BallotScannerJammedException


class ECountMachineTest(unittest.TestCase):

    def setUp(self):
        self.candidates = ['Alice', 'Bob', 'Charlie']
        self.ballot_scanner = BallotScanner(candidates=self.candidates)

        self.ballots = [
            Ballot('1', self.candidates),
            Ballot('2', self.candidates),
            Ballot('3', self.candidates)
        ]

    def test_load_ballots(self):
        self.ballot_scanner.load_ballots(self.ballots)
        self.assertEquals(self.ballot_scanner.input_tray, self.ballots)

    def test_scan_no_errors(self):

        random_mock = Mock(spec=Random)
        random_mock.random = Mock(side_effect=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0])

        self.ballot_scanner.load_ballots(self.ballots)
        self.ballot_scanner.start_batch('1', 3)
        self.ballot_scanner.scan_ballots(random_mock)

        self.assertEquals(self.ballot_scanner.accept_tray, self.ballots)
        # self.assertEquals(self.ballot_scanner.current_vote_batch.votes, [Vote([None, None, None])] * 3)

    def create_jam(self):
        random_mock = Mock(spec=Random)
        random_mock.random = Mock(side_effect=[1.0, 1.0, 1.0, 1.0, 0.0])

        self.ballot_scanner.load_ballots(self.ballots)
        self.ballot_scanner.start_batch('1', 3)
        try:
            self.ballot_scanner.scan_ballots(random_mock)
        except BallotScannerJammedException:
            pass

    def test_create_jam_leaves_accept_tray(self):
        self.create_jam()
        self.assertEquals(self.ballot_scanner.accept_tray, self.ballots[0:2])

    def test_clear_jammed_ballot(self):
        self.create_jam()
        jammed_ballot = self.ballot_scanner.remove_jammed_ballot()
        self.assertEquals(self.ballots[2], jammed_ballot)





