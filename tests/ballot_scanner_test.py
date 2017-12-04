"""
@author twsswt
"""

import unittest

from mock import Mock

from random import Random

from ecounting_workflow import Ballot, BallotScanner, BallotScannerJammedException, VoteDatabase


class BallotScannerTest(unittest.TestCase):

    def setUp(self):
        self.candidates = ['Alice', 'Bob', 'Charlie']

        def mock_record(batch):
            self.vote_batch = batch

        self.vote_database = Mock(spec=VoteDatabase)
        self.vote_database.record = Mock(side_effect=mock_record)

        self.ballot_scanner = BallotScanner(candidates=self.candidates, vote_database=self.vote_database)

        self.ballots = [
            Ballot('1', self.candidates),
            Ballot('2', self.candidates),
            Ballot('3', self.candidates)
        ]

    def test_load_ballots(self):
        self.ballot_scanner.load_ballots(self.ballots)
        self.assertEquals(self.ballot_scanner.retrieve_ballots_from_input_tray(), self.ballots)

    def test_scan_no_errors(self):
        random_mock = Mock(spec=Random)
        random_mock.random = Mock(side_effect=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0])

        self.ballot_scanner.load_ballots(self.ballots)
        self.ballot_scanner.start_batch('1', 3)
        self.ballot_scanner.scan_ballots(random_mock)

        self.assertEquals(self.ballot_scanner.retrieve_ballots_from_accept_tray(), self.ballots)

    def test_finish_vote_batch(self):
        random_mock = Mock(spec=Random)
        random_mock.random = Mock(side_effect=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0])

        self.ballot_scanner.load_ballots(self.ballots)
        self.ballot_scanner.start_batch('1', 3)
        self.ballot_scanner.scan_ballots(random_mock)
        self.ballot_scanner.finish_batch()

        actual = map (lambda vote: vote.preferences, self.vote_batch.votes)

        expected = [[None] * 3] * 3

        self.assertEquals(expected, actual)

    def test_create_jam_leaves_accept_tray(self):
        random_mock = Mock(spec=Random)
        random_mock.random = Mock(side_effect=[1.0, 1.0, 1.0, 1.0, 0.0])

        self.ballot_scanner.load_ballots(self.ballots)
        self.ballot_scanner.start_batch('1', 3)
        try:
            self.ballot_scanner.scan_ballots(random_mock)
        except BallotScannerJammedException:
            pass
        self.assertEquals(self.ballot_scanner.retrieve_ballots_from_accept_tray(), self.ballots[0:2])

    def test_clear_jammed_ballot(self):
        random_mock = Mock(spec=Random)
        random_mock.random = Mock(side_effect=[0.0])

        self.ballot_scanner.load_ballots(self.ballots)
        self.ballot_scanner.start_batch('1', 3)
        try:
            self.ballot_scanner.scan_ballots(random_mock)
        except BallotScannerJammedException:
            pass
        jammed_ballot = self.ballot_scanner.remove_jammed_ballot()
        self.assertEquals(self.ballots[0], jammed_ballot)

    def test_reject_papers(self):
        random_mock = Mock(spec=Random)
        random_mock.random = Mock(side_effect=[1.0, 0.0, 1.0, 0.0, 1.0, 0.0])

        self.ballot_scanner.load_ballots(self.ballots)
        self.ballot_scanner.start_batch('1', 3)
        try:
            self.ballot_scanner.scan_ballots(random_mock)
        except BallotScannerJammedException:
            pass

        self.assertEquals(self.ballots, self.ballot_scanner.retrieve_ballots_from_reject_tray())



