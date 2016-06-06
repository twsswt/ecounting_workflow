import unittest

from mock import Mock

from random import Random

from ecounting_workflow.ecount_system import BallotScanner, ElectoralReformServer, Vote, VoteDatabase


class ElectoralReformServerTest(unittest.TestCase):

    def setUp(self):
        self.vote_database=Mock(spec=VoteDatabase)
        self.electoral_reform_server = ElectoralReformServer(self.vote_database, 2)

    def test_stv_gregory_method_elect_alice_then_bob(self):

        test_votes = [
            Vote(['Alice', 'Bob', 'Charlie']),
            Vote(['Alice', 'Bob', 'Charlie']),
            Vote(['Alice', 'Charlie', 'Bob']),
            Vote(['Alice', 'Charlie', 'Bob'])
        ]

        self.vote_database.votes = set(test_votes)

        random_mock = Mock(spec=Random)
        random_mock.sample = Mock(side_effect=[
            test_votes[0:2], test_votes[0:1]
        ])

        self.assertEquals({'Alice', 'Bob'}, set(self.electoral_reform_server.get_election_result(random_mock).keys()))


class ECountMachineTest(unittest.TestCase):

    def setUp(self):
        self.ecount_machine = BallotScanner()



if __name__ == '__main__':
    unittest.main()
