"""
@author tws
"""


class Vote(object):

    def __init__(self, preferences=list()):
        self.preferences = list(preferences)

    def __repr__(self):
        return "v%s" % self.preferences


class VoteBatch(object):

    def __init__(self, batch_id, expected_size):
        self.batch_id = batch_id
        self._expected_size = expected_size

        self._votes = list()

    def add(self, vote):
        self._votes.append(vote)

    @property
    def votes(self):
        return self._votes

    @property
    def expected_size(self):
        return self._expected_size

    @property
    def actual_size(self):
        return len(self.votes)
