"""
@author twsswt
"""

from .vote import Vote


class BallotImage(object):

    def __init__(self, ballot, scanned_preferences):
        self.ballot = ballot
        self.scanned_preferences = scanned_preferences

    @property
    def vote(self):
        ranking = map(lambda t: t[1], sorted(filter(lambda t: t[0] is not None, zip(self.scanned_preferences, self.ballot.candidates))))
        return Vote(ranking)

    def adjust_preference(self):
        pass


class BallotImageBatch(object):

    def __init__(self, batch_id, expected_size):
        self.batch_id = batch_id
        self._expected_size = expected_size

        self._ballot_images = list()

    def add(self, ballot_image):
        self._ballot_images.append(ballot_image)

    @property
    def ballot_images(self):
        return self._ballot_images

    @property
    def expected_size(self):
        return self._expected_size

    @property
    def actual_size(self):
        return len(self.ballot_images)
