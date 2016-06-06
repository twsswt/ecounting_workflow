"""
@author twsswt
"""

from sortedcontainers.sortedset import SortedSet

from .ballot import Ballot


class Vote(object):

    def __init__(self, preferences=list()):
        self.preferences = preferences

    def __repr__(self):
        return "v%s" % self.preferences


class VoteBatch(object):

    def __init__(self, votes):
        self.votes = votes


class BallotScannerJammedException(object):

    def __init__(self, ballot_scanner):
        self.ballot_scanner = ballot_scanner


class BallotScanner(object):

    def __init__(self, vote_database=None, rate=1, scan_char_map=lambda p: p):
        self.vote_database = vote_database
        self.rate = rate
        self.scan_char_map = scan_char_map

        self.current_batch_id = None
        self.recorded_votes = list()
        self.input_tray = list()
        self.reject_tray = list()
        self.accept_tray = list()
        self.jammed_ballot = None

    def start_batch(self, batch_id):
        self.current_batch_id = batch_id

    def finish_batch(self):
        self.recorded_votes = list()
        self.current_batch_id = None
        self.vote_database.record_batch(VoteBatch(self.current_batch_id, self.recorded_votes))

    def _scan_ballot(self, random):
        if self.jammed:
            raise BallotScannerJammedException(self)
        elif random.random() < p_jam:
            self.jammed_ballot = self.input_tray.pop()
            raise BallotScannerJammedException(self)
        elif random.random() < 


    def scan_ballots(self, random):

        while len(self.input_tray) is not 0:
            self._scan_ballot(random)

    def clear_jam(self):
        jammed_ballot = self.jammed_ballot
        self.jammed_ballot = None
        return jammed_ballot


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
        while len(self.largest_pile[1]) < self.quota and len(self.eligible > 1):
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
