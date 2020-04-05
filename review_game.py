import csv
import random
from argparse import ArgumentParser
from collections import defaultdict
from sys import stdout


def _map_bins_to_labels(bins):
    """
    Maps integers 0-99 to a label according to the distribution specified in `bins`.

    Example:


    bins = [10, 20] # implies bin sizes of  10 - 20 - 70
      maps to => [0]*10 + [1]*20 + [2]*70

    Note that if the integers in `bins` don't add up to 100, this function will fill in the remaining difference with a
    new label

    :param bins: A list of integers from 0-100. Each value specifies how many times the label for the bin is repeated
    :return:
    """
    labels = [len(bins)] * 100
    label = 0
    i = 0
    for bin in bins:
        for _ in range(0, bin):
            labels[i] = label
            i += 1
        label += 1

    return labels


def _calculate_sample_label_monte_carlos(sample_size, bins):
    """
    Creates a mapping between position in a sample of `sample_size` and a rating distribution defined by `bins`

    This uses a monte carlo process to do this:
    1. Create an arbitrarily large population according to the distribution in `bins`
    2. Sample the population at `sample_size` number of intervals that are evently spaced out
    3. Repeat above a sufficient number of trials and take the average label at each sample position as the sample
    label

    :param sample_size:
    :param bins:
    :return:
    """
    sample_values = defaultdict(lambda: 0)
    for _ in range(0, 100):
        population = _generate_population(bins=bins, population_size=1000)
        population.sort()
        chunk_size = len(population) / sample_size
        for i in range(0, sample_size):
            sample_values[i] += population[int(i * chunk_size + chunk_size / 2)]

    return [int(round(sample_idx / 100)) for key, sample_idx in sample_values.items()]


def _calculate_sample_labels_oversample(sample_size, bins, population_size=10000):
    """
    Creates a mapping between position in a sample of `sample_size` and a rating distribution defined by `bins`

    This uses oversampling to do this:
    1. Create an arbitrarily large population according to the distribution in `bins`
    2. Sample the population at `sample_size` number of intervals that are evently spaced out

    :param sample_size:
    :param bins:
    :param population_size:
    :return:
    """
    population = _generate_population(bins=bins, population_size=population_size)
    population.sort()
    sample_labels = []
    chunk_size = len(population) / sample_size
    for i in range(0, sample_size):
        sample_labels.append(population[int(i * chunk_size + chunk_size / 2)])

    return sample_labels


def _generate_population(bins, population_size):
    """
    Generates a population of `population_size` with the ratings distribution specified by `bins`.

    :param bins:
    :param population_size:
    :return:
    """
    range_labels = _map_bins_to_labels(bins=bins)
    population = []

    # Apply the `range_labels` to `population_size` random numbers between 0-100
    for _ in range(0, population_size):
        bin = range_labels[random.randint(0, len(range_labels) - 1)]
        population.append(bin)
    return population


def _rate_population(population, sample_size, get_sample_labels):
    """
    Goes through the population and applies ratings to the population usings groups of size `sample_size`
    :param population:
    :param sample_size:
    :param get_sample_labels:
    :return:
    """
    ratings = [0] * len(population)

    # `sample_labels` is basically a lookup table that says what rating to apply to what individual in the sample. This
    # lookup table assumes both the labels and the sample are sorted
    # Reverse the sorting so that we apply the highest ratings to first
    sample_labels_high_to_low = list(get_sample_labels(sample_size=sample_size))
    sample_labels_high_to_low.reverse()

    # Go through the population in chunks of sample_size
    i = 0
    while True:

        # Get the indexes of the sample in sorted order
        sample = population[i: min(len(population), i + sample_size)]
        sorted_sample_indices = [i[0] for i in sorted(enumerate(sample), key=lambda x: x[1])]

        # Reverse so we apply ratings to the top individuals in the sample first
        sorted_sample_indices.reverse()

        # The last iteration of this loop may consider a group smaller than `sample_size`, so we need to get a
        # different set of sample_labels for this group
        if len(sample) != sample_size:
            sample_labels_high_to_low = list(get_sample_labels(sample_size=len(sample)))
            sample_labels_high_to_low.reverse()

        # Apply the sample ratings
        for sample_rating, sample_idx in zip(sample_labels_high_to_low, sorted_sample_indices):
            ratings[i + sample_idx] = sample_rating

        # Go to the next chunk
        i += sample_size

        if i >= len(population):
            break

    return ratings


def _score_ratings(population, ratings, production, correct_score=100, underestimate_score=-100,
                   over_estimate_score=50):
    """
    Apply a simple model to score how well the ratings represents the true ratings of the population.

    :param population:
    :param ratings:
    :param production:
    :param correct_score:
    :param underestimate_score:
    :param over_estimate_score:
    :return:
    """
    scores = []
    for employee, rating in zip(population, ratings):
        if rating < employee:
            scores.append(production[employee] * underestimate_score)
        elif rating > employee:
            scores.append(production[employee] * over_estimate_score)
        else:
            scores.append(production[employee] * correct_score)

    return scores


def _get_rating_accuracy_stats(population, ratings):
    """
    Calculate how accurate our ratings were.

    :param population:
    :param ratings:
    :return:
    """
    num_overestimates = 0
    num_underestimates = 0
    num_correct = 0
    for employee, rating in zip(population, ratings):
        if rating < employee:
            num_underestimates += 1
        elif rating > employee:
            num_overestimates += 1
        else:
            num_correct += 1

    return num_underestimates, num_correct, num_overestimates


def calculate_monte_carlo_stats(scores, rating_accuracy):
    """
    Assumes `scores` and `rating_counts` have stats for the same configurations. Collates the monte carlo stats for
    the simulation runs

    :param scores:
    :param rating_accuracy:
    :return:
    """
    averages = []

    for key, stats in scores.items():
        average_score = sum(stats) / len(stats)
        average_underestimates = sum([stats[0] for stats in rating_accuracy[key]]) / len(stats)
        average_correct = sum([stats[1] for stats in rating_accuracy[key]]) / len(stats)
        average_overestimates = sum([stats[2] for stats in rating_accuracy[key]]) / len(stats)
        averages.append(list(key) + [average_score, average_underestimates, average_correct, average_overestimates])

    return averages


def _sample_labels_calculator(population_size, bins):
    """
    Returns a function that gets and memoizes sample label mappings for a distribution specified by `bins`
    :param population_size:
    :param bins:
    :return:
    """
    sample_labels = {}

    def get_sample_labels(sample_size):
        if sample_size not in sample_labels:
            sample_labels[sample_size] = _calculate_sample_labels_oversample(
                sample_size=min(sample_size, population_size),
                bins=bins,
                population_size=max(100000,
                                    population_size * 100))
        return sample_labels[sample_size]

    return get_sample_labels


def simulate_ratings(performance_bins, population_size, sample_sizes, rating_bins, payoffs, production,
                     num_repetitions=1):
    """
    Simulate all of the configurations specified in the arguments and return the aggregated states for the simulations

    :param performance_bins:
    :param population_size:
    :param sample_sizes:
    :param rating_bins:
    :param payoffs:
    :param production:
    :param num_repetitions:
    :return:
    """
    rating_scores = defaultdict(list)
    rating_accuracy = defaultdict(list)

    # Precompute the distributions for the different sample sizes
    get_sample_labels = _sample_labels_calculator(population_size=population_size, bins=rating_bins)
    for sample_size in sample_sizes:
        get_sample_labels(sample_size=sample_size)

    # Repeat the simulation of each configuration `num_repetitions` times
    for _ in range(0, num_repetitions):

        # Random variable: the true distribution of ratings varies from run to run
        population = _generate_population(bins=performance_bins, population_size=population_size)

        # Now see how our stats are affected by rating this population using different sample sizes
        for sample_size in sample_sizes:
            ratings = _rate_population(population=population, sample_size=sample_size,
                                       get_sample_labels=get_sample_labels)

            # These stats don't change by payoff functions
            num_underestimates, num_correct, num_overestimates = _get_rating_accuracy_stats(population=population,
                                                                                            ratings=ratings)

            # Score ratings using different payoff functions. Collate stats by simulation configuration
            for payoff in payoffs:
                run_configuration = tuple([sample_size] + list(payoff))

                scores = \
                    _score_ratings(population, ratings,
                                   production=production,
                                   underestimate_score=payoff[0],
                                   over_estimate_score=payoff[2],
                                   correct_score=payoff[1])

                rating_accuracy[run_configuration].append((num_underestimates, num_correct, num_overestimates))
                rating_scores[run_configuration].append(sum(scores))

    return rating_scores, rating_accuracy


def print_simulation(f, scores):
    writer = csv.writer(f)
    for score in scores:
        writer.writerow(score)


def main(args):
    if args.sample_sizes:
        sample_sizes = [int(s) for s in args.sample_sizes]
    else:
        sample_sizes = [5]
        while sample_sizes[-1] * 2 < int(args.population / 2):
            sample_sizes.append(sample_sizes[-1] * 2)

        # always include half the population and the entire population
        sample_sizes += [int(args.population / 2), args.population]

    # payoffs = [(-1, 1, .5), (0, 1, .5), (0, 0, 0), (-.5, 1, .5), (-.25, 1, .5), (-.25, .5, .25)]
    payoffs = [(.5, 1.2, 1)]

    rating_scores, rating_accuracy = simulate_ratings(performance_bins=args.performance_bins,
                                                      population_size=args.population,
                                                      sample_sizes=sample_sizes,
                                                      rating_bins=args.rating_bins,
                                                      payoffs=payoffs,
                                                      production=args.production,
                                                      num_repetitions=args.num_repetitions)

    results = calculate_monte_carlo_stats(scores=rating_scores, rating_accuracy=rating_accuracy)
    print_simulation(stdout, results)


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Demonstrates the effect of proper sample size usage in the context of a game with cost and payoff")

    parser.add_argument("--performance-bins", type=int, nargs='+', default=[5, 10, 50, 25, 10],
                        help="The true distribution of the population's performance")
    parser.add_argument("--rating-bins", type=int, nargs='+', default=[5, 10, 50, 25, 10],
                        help="The distribution the stack ranking policy assumes")
    parser.add_argument("--sample-sizes", type=int, nargs='+',
                        help="The sizes of stack ranking groups to test")
    parser.add_argument("--population", type=int, default=200,
                        help="The total size of the organization being stack ranked")
    parser.add_argument("--num-repetitions", type=int, default=100,
                        help="The number of Monte Carlo runs to use")
    parser.add_argument("--production", type=int, nargs='+', default=[1.05, 1.1, 1.15, 1.2, 1.25],
                        help="The true production of employees in each performance bin")

    args = parser.parse_args()

    main(args)
