"""
@author twsswt
"""

from sortedcontainers.sortedset import SortedSet


class VoteDatabase(object):

    def __init__(self):
        self.batches = SortedSet(key=lambda b: b.id)
        pass

    def record(self, vote_batch):
        self.batches.add(vote_batch)

    @property
    def votes(self):
        return reduce(lambda a, b: a.votes.union(b.votes), self.batches, set())
