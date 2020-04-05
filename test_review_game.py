import pytest

from review_game import _map_bins_to_labels, _generate_population, _calculate_sample_labels_oversample, \
    _rate_population, _score_ratings, _sample_labels_calculator, calculate_monte_carlo_stats, \
    _get_rating_accuracy_stats, simulate_ratings


def test__map_bins_to_labels():
    labels = _map_bins_to_labels(bins=[5, 10])
    assert [0] * 5 + [1] * 10 + [2] * 85 == labels

    labels = _map_bins_to_labels(bins=[100])
    assert [0] * 100 == labels

    labels = _map_bins_to_labels(bins=[])
    assert [0] * 100 == labels

    labels = _map_bins_to_labels(bins=[0])
    assert [1] * 100 == labels


def test__generate_population():
    population = _generate_population(bins=[0], population_size=10)
    assert [1] * 10 == population


def test__calculate_sample_label_oversample():
    labels = _calculate_sample_labels_oversample(sample_size=10, bins=[10, 20])
    assert [0] + [1] * 2 + [2] * 7 == labels

    # round down to zero
    labels = _calculate_sample_labels_oversample(sample_size=10, bins=[5, 20])
    assert (0 * 5 + 20 * 1 + 75 * 2) / 100 == pytest.approx(sum(labels) / len(labels), .1)

    # round up
    labels = _calculate_sample_labels_oversample(sample_size=10, bins=[15, 20])
    assert (0 * 15 + 20 * 1 + 65 * 2) / 100 == pytest.approx(sum(labels) / len(labels), .1)


def test__rate_population():
    population = [2, 0, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2]

    get_sample_labels = _sample_labels_calculator(population_size=len(population), bins=[0, 20])
    ratings = _rate_population(population=population, sample_size=5, get_sample_labels=get_sample_labels)
    assert [2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2] == ratings

    get_sample_labels = _sample_labels_calculator(population_size=len(population), bins=[20, 20])
    ratings = _rate_population(population=population, sample_size=5, get_sample_labels=get_sample_labels)
    assert [2, 0, 1, 2, 2, 0, 1, 2, 2, 2, 1, 2] == ratings

    population = [2, 0]
    get_sample_labels = _sample_labels_calculator(population_size=len(population), bins=[15, 20])
    ratings = _rate_population(population=population, sample_size=5, get_sample_labels=get_sample_labels)
    assert [2, 1] == ratings


def test__score_ratings():
    results = _score_ratings(population=[10, 10, 10, 10],
                             ratings=[10, 9, 11, 10],
                             production=[1.05, 1.1, 1.15, 1.2, 1.25],
                             correct_score=10,
                             underestimate_score=-10,
                             over_estimate_score=5)
    assert [10, -10, 5, 10] == results


def test__get_rating_accuracy_stats():
    assert (1, 2, 1) == _get_rating_accuracy_stats(population=[10, 10, 10, 10],
                                                   ratings=[10, 9, 11, 10])


def test_calculate_monte_carlo_stats():
    rating_scores = {(1, 2): [1, 3, 7, 13], (2, 2): [1, 3, 7, 130]}
    rating_accuracy_stats = {(1, 2): [(1, 2, 3), (3, 6, 9), (7, 14, 21), (13, 26, 39)],
                     (2, 2): [(1, 2, 3), (3, 6, 9), (7, 14, 21), (130, 260, 390)]}
    averages = calculate_monte_carlo_stats(scores=rating_scores, rating_accuracy=rating_accuracy_stats)
    assert [[1, 2, 6.0, 6.0, 12.0, 18.0], [2, 2, 35.25, 35.25, 70.5, 105.75]] == sorted(averages)


def test_simulate_ratings():
    rating_scores, rating_accuracy = simulate_ratings([20, 20], population_size=5, sample_sizes=[3, 5],
                                                      rating_bins=[20, 20],
                                                      payoffs=[(-1, 1, 0), (0, 1, 0)],
                                                      num_repetitions=1,
                                                      production=[1.05, 1.1, 1.15, 1.2, 1.25])
    averages = calculate_monte_carlo_stats(scores=rating_scores, rating_accuracy=rating_accuracy)
    averages.sort()

    # Make sure we are simulating all the configurations
    assert 4 == len(averages)
    assert [3, -1, 1, 0] == averages[0][0:4] and [3, 0, 1, 0] == averages[1][0:4]
    assert [5, -1, 1, 0] == averages[2][0:4] and [5, 0, 1, 0] == averages[3][0:4]
