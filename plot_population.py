import matplotlib.pyplot as plt
import math
from review_game import _generate_population


def main():
    counts = [8, 4, 2, 1]
    sizes = [8, 16, 32, 64]

    for count, size in zip(counts, sizes):
        rows = cols = count
        sample_size = size
        population = _generate_population(bins=[5, 10, 50, 25, 10], population_size=rows * cols * sample_size)

        fig = draw_samples(population, sample_size, rows, cols)
        fig.savefig('data/population_{}.eps'.format(size), format='eps')


def draw_samples(population, sample_size, rows, cols):
    fig, axs = plt.subplots(ncols=cols, nrows=rows, sharey=True, sharex=True, squeeze=False)
    fig.set_size_inches(3, 3)
    fig.text(.51, .91, 'Sample Size = {}'.format(sample_size), ha='center', va='center')

    for i, row in enumerate(axs):
        for j, ax in enumerate(row):
            offset = i * (cols * sample_size) + j * sample_size

            sample = sorted([x + 0 for x in population[offset:offset + sample_size]])
            average = round(sum(sample) / len(sample), 1)

            # bars
            ax.bar(range(0, sample_size), sample, align='edge', width=1, color='#c6d9ec')
            ax.set_xlim(0, sample_size)
            ax.set_ylim(0, 5)
            ax.set_yticklabels([])
            ax.set_xticklabels([])
            ax.set_facecolor('#ecf2f9')

            # average
            ax.text(sample_size / 2, 5 / 2, average, ha='center', va='center', style='normal',
                    fontdict={'fontweight': 500, 'color': '#000000', 'fontsize': 'smaller'})

            for ax in row[:]:
                ax.yaxis.set_visible(False)
                ax.xaxis.set_visible(False)

            fig.subplots_adjust(wspace=0, hspace=0)
    return fig


def draw_averages(population, sample_size, rows, cols):
    fig, axs = plt.subplots(ncols=cols, nrows=rows, sharey=True, sharex=True, squeeze=False)
    fig.set_size_inches(3, 3)
    fig.text(.51, .91, 'Sample Size = {}'.format(sample_size), ha='center', va='center')

    for i, row in enumerate(axs):
        for j, ax in enumerate(row):
            offset = i * (cols * sample_size) + j * sample_size

            sample = sorted([x + 0 for x in population[offset:offset + sample_size]])
            average = round(sum(sample) / len(sample), 1)

            # bars
            ax.bar(range(0, sample_size), sample, align='edge', width=1, color='#c6d9ec')
            ax.set_xlim(0, sample_size)
            ax.set_ylim(0, 5)
            ax.set_yticklabels([])
            ax.set_xticklabels([])
            ax.set_facecolor('#ecf2f9')

            # average
            ax.text(sample_size / 2, 5 / 2, average, ha='center', va='center', style='normal',
                    fontdict={'fontweight': 500, 'color': '#000000', 'fontsize': 'smaller'})

            for ax in row[:]:
                ax.yaxis.set_visible(False)
                ax.xaxis.set_visible(False)

            fig.subplots_adjust(wspace=0, hspace=0)
    return fig


if __name__ == '__main__':
    main()
