import pyccl as ccl
from ..base_calculator import TheoryCalculator
import numpy as np


class StackedClusterTheoryCalculator(TheoryCalculator):
    name = "stackedcluster"
    statistic_types = ["CL_counts","gamma_t"]
