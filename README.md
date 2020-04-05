# Stack Ranking Simulator
Simulates how changing the way you implement employee stack ranking affects how inaccurate stack ranking is.

These scripts were used to generate the data and the plots in the medium post, [How to Stack Rank Your Organization
](https://medium.com/@imprisonevery1/how-to-stack-rank-your-organization-a5cb6d5c9149).

They are Monte Carlo simulations, meaning each configuration is simulated a number of times are the results are averaged across those repetitions. The population's true performance is drawn randomly according to the true distribution specified in the simulation configuration.

# Scripts

* `review_game.py`: This script generates the data that shows review accuracy for different stack ranking group sizes. Use `-h` to see available arguments. Use `pytest -svv` to run the tests.
* `plot_population.py`: This script plots the variation of performance averages for different stack ranking group sizes

# Usage

```
usage: review_game.py [-h]
                      [--performance-bins PERFORMANCE_BINS [PERFORMANCE_BINS ...]]
                      [--rating-bins RATING_BINS [RATING_BINS ...]]
                      [--sample-sizes SAMPLE_SIZES [SAMPLE_SIZES ...]]
                      [--population POPULATION]
                      [--num-repetitions NUM_REPETITIONS]
                      [--production PRODUCTION [PRODUCTION ...]]

Demonstrates the effect of proper sample size usage in the context of a game
with cost and payoff

optional arguments:
  -h, --help            show this help message and exit
  --performance-bins PERFORMANCE_BINS [PERFORMANCE_BINS ...]
                        The true distribution of the population's performance
  --rating-bins RATING_BINS [RATING_BINS ...]
                        The distribution the stack ranking policy assumes
  --sample-sizes SAMPLE_SIZES [SAMPLE_SIZES ...]
                        The sizes of stack ranking groups to test
  --population POPULATION
                        The total size of the organization being stack ranked
  --num-repetitions NUM_REPETITIONS
                        The number of Monte Carlo runs to use
  --production PRODUCTION [PRODUCTION ...]
                        The true production of employees in each performance
                        bin
```

```
pip install -r requirements.txt
python review_game.py --sample-sizes 8 16 32 64 128 # script that generates the data
python plot_population.py # script that creates population boxes
```

## Sample Output of `review_game.py`

### Columns

* Run Configuration: Group Size
* Run Configuration: Score for underestimating someone's rating
* Run Configuration: Score for correctly estimating someone's rating
* Run Configuration: Score for overestimating someone's rating
* Output: Total average score for the run configuration
* Output: Average number of underestimated ratings
* Output: Average number of correct ratings
* Output: Average number of overestimated ratings

Sample output for a 200 person org with stack rank groups of 5, 10, 20, 40, 80, 100, and 200:

```
5,0.5,1.2,1,228.53114999999968,50.21,112.42,37.37 # Stats when stack ranking groups of 5
10,0.5,1.2,1,253.08149999999958,19.05,136.6,44.35
20,0.5,1.2,1,253.97154999999958,24.32,153.63,22.05
40,0.5,1.2,1,260.3488999999994,18.34,165.8,15.86
80,0.5,1.2,1,264.6153999999994,14.3,173.9,11.8
100,0.5,1.2,1,266.9551999999995,12.08,178.33,9.59
200,0.5,1.2,1,270.44119999999947,8.78,184.93,6.29 # Stats when stack ranking groups of 200
```    
    
    
