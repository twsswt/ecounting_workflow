"""
@author twsswt
"""

from .ballot_image import BallotImage, BallotImageBatch


class BallotScannerJammedException(Exception):

    def __init__(self, ballot_scanner):
        self.ballot_scanner = ballot_scanner


class UnReadBallotException(Exception):

    def __init__(self, ballot_scanner):
        self.ballot_scanner = ballot_scanner


class BallotScanner(object):

    def __init__(self, vote_database=None, candidates=list(), rate=1, p_jam=0.01, p_reject=0.01, scan_char_map=lambda p: p):
        self.vote_database = vote_database
        self.candidates = candidates

        self.rate = rate
        self.p_jam = p_jam
        self.p_reject = p_reject

        self.scan_char_map = scan_char_map

        self.current_ballot_image_batch = None

        self._input_tray = list()
        self._reject_tray = list()
        self._accept_tray = list()
        self._jammed_ballot = None

    @property
    def jammed(self):
        return self._jammed_ballot is not None

    def start_batch(self, batch_id, expected_size):
        self.current_ballot_image_batch = BallotImageBatch(batch_id, expected_size)

    def load_ballots(self, ballots):
        self._input_tray.extend(ballots)

    @staticmethod
    def _retrieve_ballots_from_tray(tray):
        result = list(tray)
        del tray[:]
        return result

    def retrieve_ballots_from_input_tray(self):
        return self._retrieve_ballots_from_tray(self._input_tray)

    def retrieve_ballots_from_reject_tray(self):
        return self._retrieve_ballots_from_tray(self._reject_tray)

    def retrieve_ballots_from_accept_tray(self):
        return self._retrieve_ballots_from_tray(self._accept_tray)

    def remove_jammed_ballot(self):
        jammed_ballot = self._jammed_ballot
        self._jammed_ballot = None
        return jammed_ballot

    def _ocr_ballot(self, ballot, random):
        if random.random() < self.p_reject:
            raise UnReadBallotException(self)
        else:
            scanned_preferences = [None] * len(self.candidates)
            for ballot_preference in ballot.preferences:
                scanned_preferences.append(self.scan_char_map(ballot_preference))
            return BallotImage(ballot, scanned_preferences)

    def _scan_ballot(self, random):
        if self.jammed:
            raise BallotScannerJammedException(self)
        else:
            next_ballot = self._input_tray.pop(0)
            if random.random() < self.p_jam:
                self._jammed_ballot = next_ballot
                raise BallotScannerJammedException(self)
            else:
                try:
                    ballot_image = self._ocr_ballot(next_ballot, random)
                    self.current_ballot_image_batch.add(ballot_image)
                    self._accept_tray.append(next_ballot)
                except UnReadBallotException:
                    self._reject_tray.append(next_ballot)

    def scan_ballots(self, random):
        while len(self._input_tray) is not 0:
            self._scan_ballot(random)

    def finish_batch(self):
        self.vote_database.record(self.current_ballot_image_batch)
        self.current_ballot_image_batch = None
