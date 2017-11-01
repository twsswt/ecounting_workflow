import unittest

from ecounting_workflow.ballot import Ballot


class BallotTestCase(unittest.TestCase):

    def setUp(self):
        self.ballot = Ballot('1', ['Alice', 'Bob', 'Charles'])

    def test_partial_mark(self):
        self.ballot.mark('Alice', 1)
        self.assertEqual(self.ballot.preferences, [1, None, None])

    def test_full_mark_ordered(self):
        self.ballot.mark('Alice', 1)
        self.ballot.mark('Bob', 2)
        self.ballot.mark('Charles', 3)

        self.assertEqual(self.ballot.preferences, [1, 2, 3])

    def test_full_mark_unordered(self):
        self.ballot.mark('Charles', 2)
        self.ballot.mark('Alice', 3)
        self.ballot.mark('Bob', 1)

        self.assertEqual(self.ballot.preferences, [3, 1, 2])




if __name__ == '__main__':
    unittest.main()