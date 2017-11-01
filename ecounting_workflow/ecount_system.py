"""
@author twsswt
"""

from sortedcontainers.sortedset import SortedSet

from .ballot import Ballot


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

        self.current_vote_batch = None

        self.input_tray = list()
        self.reject_tray = list()
        self.accept_tray = list()
        self.jammed_ballot = None

    @property
    def jammed(self):
        return self.jammed_ballot is not None

    def start_batch(self, batch_id, expected_size):
        self.current_vote_batch = VoteBatch(batch_id, expected_size)

    def load_ballots(self, ballots):
        self.input_tray.extend(ballots)

    @staticmethod
    def _retrieve_ballots_from_tray(tray):
        result = list(tray)
        del tray[:]
        return result

    def retrieve_ballots_from_input_tray(self):
        return self._retrieve_ballots_from_tray(self.input_tray)

    def retrieve_ballots_from_reject_tray(self):
        return self._retrieve_ballots_from_tray(self.reject_tray)

    def retrieve_ballots_from_accept_tray(self):
        return self._retrieve_ballots_from_tray(self.accept_tray)

    def remove_jammed_ballot(self):
        jammed_ballot = self.jammed_ballot
        self.jammed_ballot = None
        return jammed_ballot

    def _ocr_ballot(self, ballot, random):
        if random.random() < self.p_reject:
            raise UnReadBallotException(self)
        else:
            vote_preferences = [None] * len(self.candidates)
            for candidate, ballot_preference in zip(self.candidates, ballot.preferences):
                scanned_preference = self.scan_char_map(ballot_preference)
                if type(scanned_preference) is int:
                    vote_preferences[scanned_preference] = candidate
            return Vote(vote_preferences)

    def _scan_ballot(self, random):
        if self.jammed:
            raise BallotScannerJammedException(self)
        else:
            next_ballot = self.input_tray.pop(0)
            if random.random() < self.p_jam:
                self.jammed_ballot = next_ballot
                raise BallotScannerJammedException(self)
            else:
                try:
                    vote = self._ocr_ballot(next_ballot, random)
                    self.current_vote_batch.add(vote)
                    self.accept_tray.append(next_ballot)
                except UnReadBallotException:
                    self.reject_tray.append(next_ballot)

    def scan_ballots(self, random):
        while len(self.input_tray) is not 0:
            self._scan_ballot(random)

    def finish_batch(self):
        self.vote_database.record_batch(self.current_vote_batch)
        self.current_vote_batch = None


class VoteDatabase(object):

    def __init__(self):
        self.batches = SortedSet(key=lambda b: b.id)
        pass

    def record_vote_batch(self, vote_batch):
        self.batches.add(vote_batch)

    @property
    def votes(self):
        return reduce(lambda a, b: a.votes.union(b.votes), self.batches, set())


class VotePiles(object):

    def __init__(self, votes, num_positions):
        self.votes = votes
        self.num_positions = num_positions

        self.eligible = {key: set() for key in self.candidates}
        self.eliminated = dict()
        self.elected = dict()

    @property
    def quota(self):
        return int(round(1.0 * len(self.votes) / (self.num_positions + 1), 0))

    @property
    def candidates(self):
        return reduce(lambda v1, v2: set(v1.union(v2)), map(lambda v: v.preferences, self.votes), set())

    @property
    def largest_pile(self):
        return reduce(lambda a, b: a if len(a[1]) >= len(b[1]) else b, self.eligible.items())

    @property
    def smallest_pile(self):
        return reduce(lambda a, b: a if len(a[1]) < len(b[1]) else b, self.eligible.items())

    def distribute_votes(self, votes):

        to_remove = set()

        for vote in votes:
            n = 0
            while n < len(vote.preferences) and vote.preferences[n] not in self.eligible.keys():
                n += 1

            if n < len(vote.preferences):
                self.eligible[vote.preferences[n]].add(vote)
                to_remove.add(vote)

        votes -= to_remove

    def eliminate_losing_candidate(self):
        losing_candidate, losing_pile = self.smallest_pile
        del self.eligible[losing_candidate]
        self.distribute_votes(losing_pile)
        self.eliminated[losing_candidate] = losing_pile

    def eliminate_winning_candidate(self, random):
        while len(self.largest_pile[1]) < self.quota and len(self.eligible) > 1:
            self.eliminate_losing_candidate()

        winning_candidate, winning_pile = self.largest_pile
        surplus_votes = set(random.sample(winning_pile, len(winning_pile) - self.quota))
        winning_pile -= surplus_votes
        del self.eligible[winning_candidate]
        self.distribute_votes(surplus_votes)
        self.elected[winning_candidate] = winning_pile

    def operate(self, random):

        self.distribute_votes(set(self.votes))

        while len(self.elected) < self.num_positions and len(self.eligible) > self.num_positions - len(self.elected):
            self.eliminate_winning_candidate(random)


class ElectoralReformServer(object):

    def __init__(self, vote_database, num_positions):
        self.vote_database = vote_database
        self.num_positions = num_positions

    def get_election_result(self, random):

        piles = VotePiles(self.vote_database.votes, self.num_positions)
        piles.operate(random)

        return piles.elected
