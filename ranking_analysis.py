"""Analysis of a ranking run"""
import argparse
import csv
import sys


class RankingAnalysis:
    """Analysis of a ranking run"""
    # factor difference between two affinities for the to be significantly different
    SIGNIFICANCE_FACTOR = 10

    def __init__(self, scores, affinities):
        self.scores = scores
        self.affinities = affinities

    def perform(self):
        """Perform a ranking analysis"""
        scores = self.get_scores()
        scores = self.make_hits_unique(scores)
        hits = []
        not_found = []
        for hit in scores:
            if hit[1]:
                hits.append(hit)
            else:
                not_found.append(hit)
        affinity_map = self.get_affinities()

        rank_tuples = []
        for index, hit in enumerate(hits):
            for candidate in hit[0]:
                affinities = affinity_map[candidate]
                min_affinity = min(affinities)
                max_affinity = max(affinities)
                rank_tuples.append((index, candidate, min_affinity, max_affinity))
                print('result: {}, {}, {}, {}'.format(
                    candidate, hit[1], min_affinity, max_affinity))
        for hit in not_found:
            for candidate in hit[0]:
                affinities = affinity_map[candidate]
                min_affinity = min(affinities)
                max_affinity = max(affinities)
                rank_tuples.append((len(scores), candidate, min_affinity, max_affinity))
                print('result: {}, {}, {}, {}'.format(
                    candidate, None, min_affinity, max_affinity))
        self.compute_significant_differences(rank_tuples)

    @staticmethod
    def approx_equal(first, second):
        """first and second are approximately equal using float epsilon"""
        return abs(first - second) < sys.float_info.epsilon

    @staticmethod
    def compute_significant_differences(rank_tuples):
        """Count the number of significant differences and whether they were ranked correctly"""
        significant_differences = 0
        correct_differences = 0
        involved = set()
        for rank in rank_tuples:
            for other in rank_tuples:
                if rank == other:
                    continue
                # other affinity is significance factor higher
                if RankingAnalysis.approx_equal(other[2] / RankingAnalysis.SIGNIFICANCE_FACTOR, rank[3]) \
                        or other[2] / RankingAnalysis.SIGNIFICANCE_FACTOR > rank[3]:
                    involved.add(rank[1])
                    involved.add(other[1])
                    significant_differences += 1
                    if other[0] > rank[0]:
                        correct_differences += 1
                # other affinity is significance factor lower, epsilon scales with multiplication
                if RankingAnalysis.approx_equal(rank[2] / RankingAnalysis.SIGNIFICANCE_FACTOR, other[3]) \
                        or rank[2] / RankingAnalysis.SIGNIFICANCE_FACTOR > other[3]:
                    involved.add(rank[1])
                    involved.add(other[1])
                    significant_differences += 1
                    if other[0] < rank[0]:
                        correct_differences += 1
        # significant differences are symmetrical and counted twice
        significant_differences /= 2
        correct_differences /= 2
        print('involved: ' + ', '.join(involved))
        if significant_differences > 0:
            percentage_correct = correct_differences * 100.0 / significant_differences
            print('result: percentage correctly ranked {} ({} / {})'.format(
                percentage_correct, correct_differences, significant_differences))
        else:
            print('result: no significant differences')

    def get_scores(self):
        """Get scores from file"""
        scores = []
        with open(self.scores) as score_file:
            reader = csv.reader(score_file, delimiter='\t')
            for line in reader:
                scores.append((line[0].split('_')[0].split(','), float(line[1]) if line[1] else None))
        return scores

    @staticmethod
    def make_hits_unique(hits):
        """Filters out all duplicates based on candidate names

        This is aimed at stereoisomers. The better score duplicate/stereoisomer is
        used further.
        """
        unique_map = {}
        for hit in hits:
            key = ''.join(sorted(hit[0]))
            if key not in unique_map:
                unique_map[key] = hit
            elif hit[1] < unique_map[key][1]:
                unique_map[key] = hit
        unique_hits = []
        for hit in unique_map.values():
            unique_hits.append(hit)
        return unique_hits

    def get_affinities(self):
        """Get affinities for th ranking"""
        affinity_map = {}
        with open(self.affinities) as affinity_file:
            reader = csv.reader(affinity_file)
            for line in reader:
                name = line[0]
                value = float(line[2])
                unit = line[3]
                # change everything to nM
                if unit == 'uM':
                    value *= 1000
                elif unit == 'pM':
                    value /= 1000
                if name not in affinity_map:
                    affinity_map[name] = []
                affinity_map[name].append(value)
        return affinity_map


def main(args):
    """Main"""
    ranking_analysis = RankingAnalysis(args.scores, args.affinities)
    ranking_analysis.perform()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('scores', type=str, help='path to scores TSV')
    parser.add_argument('affinities', type=str, help='path to affinities CSV')
    main(parser.parse_args())
