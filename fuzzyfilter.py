import re
from functools import partial


class FuzzyFilter:
    """Perform fuzzy matching using provided filter function

    Example:
    fuzzy_dice = FuzzyFilter(dice_matches)
    fuzzy_dice.filter([(1, "Foo"),
                       (2, "Bar"),
                       (3, "Baz")], limit=3).matching("ba")
    Returns:
    [(2, 'Bar', 0.6666666666666666),
     (3, 'Baz', 0.6666666666666666),
     (1, 'Foo', 0.0)]

    """
    LIMIT = 10

    def __init__(self, filter_func):
        self._filter_strategy = filter_func

    def filter(self, things, limit=LIMIT):
        self.matching = partial(self._match, things, n=limit)
        return self

    def _match(self, things, thing, n=None):
        results = self._filter_strategy(thing, things)
        return results[:n] if n else results

def dice_match(search_str, col_with_ids=[(0, '')]):
    """Find Dice's coefficent of search_str for string in list of tuples

    Returns sorted list of tuples containing id, matched string, and score

    See: http://en.wikipedia.org/wiki/Dice%27s_coefficient

    """
    SCORE_IDX = 1
    THRESHOLD = 0.10

    def get_ngrams(string, n=2):
        """returns a list of n-grams for string. Default: bigrams"""
        return [string[i:i+n] for i in xrange(len(string) - 1)]

    def preformat_string(string):
        """Format string for better bigram matching"""
        s = string.lower()
        s = re.sub(r'[^a-z0-9]', '', s)
        return s

    results = []
    seen = set()
    pairs1 = get_ngrams(preformat_string(search_str))
    for row_id, s in col_with_ids:
        if row_id in seen:
            continue
        pairs2 = get_ngrams(preformat_string(s))
        union = len(pairs1) + len(pairs2)
        if not union:
            continue
        hit_count = 0
        for x in pairs1:
            for y in pairs2:
                if x == y:
                    hit_count += 1
                    break
        score = (2.0 * hit_count) / union
        if score > THRESHOLD and row_id not in seen:
            results.append((row_id, score))
            seen.add(row_id)
    return [x for x in sorted(results, key=lambda m: m[SCORE_IDX], reverse=True)]


if __name__ == "__main__":
    import timeit
    from pprint import PrettyPrinter as PP

    search_str = "Raj Langur"
    people = ['Raj Lanka', 'Raj Langur', 'Rachael Langur', 'Lankur, Raj',
              'Tom Langur', 'Ra J Langur', 'Robert Lang', 'Raj Lang']
    col_with_ids = zip(xrange(1, len(people) + 1), people)

    def test_dice():
        fuzzy_dice = FuzzyFilter(dice_match)
        return fuzzy_dice.filter(col_with_ids, limit=10).matching(search_str)

    matches = test_dice()
    PP().pprint(matches)
    print "test_dice:"
    results = timeit.repeat("test_dice()", setup="from __main__ import test_dice", repeat=1000, number=1000)
    print sum(results) / len(results)
