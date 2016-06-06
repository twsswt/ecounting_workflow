
class Ballot(object):

    def __init__(self, preferences=dict()):
        self.preferences = preferences
        pass


class BallotBatch(object):

    def __init__(self, ballots=list(), expected=0):
        self.ballots = ballots
        self.expected_= expected
        pass