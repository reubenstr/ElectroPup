#!/usr/bin/env python3

import pstats

"""
TODO: try snakeviz:
    pip install snakeviz
    snakeviz profile_results.prof

"""

stats = pstats.Stats("trajectories.prof")
stats.strip_dirs().sort_stats("cumulative").print_stats(20)
