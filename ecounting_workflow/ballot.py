"""
@author twsswt
"""


class Ballot(object):

    def __init__(self, serial_number, candidates):
        self.serial_number = serial_number
        self._preferences = { candidate:None for candidate in candidates }

    @property
    def candidates(self):
        return sorted(self._preferences.keys())

    def mark(self, preferences):

        for candidate, ranking in preferences.items():
            if self._preferences[candidate] is None:
                self._preferences[candidate] = ranking
            else:
                self.overwrite(candidate, ranking)

    def overwrite(self, candidate, ranking):
        self._preferences[candidate] = ranking

    def spoil(self, candidate, preference):
        self._preferences[candidate] = '#'

    @property
    def preferences(self):
        return map(lambda i: i[1], sorted(self._preferences.items()))

    def __str__(self):
        return "b:%s" % self.serial_number

    def __repr__(self):
        return "b:%s [%s]" % (self.serial_number, self._preferences)


class BallotBatch(object):

    def __init__(self, ballots=list(), expected=0):
        self.ballots = ballots
        self.expected_= expected
