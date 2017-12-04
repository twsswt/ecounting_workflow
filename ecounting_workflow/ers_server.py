"""
@author twsswt
"""


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
