import pyccl as ccl
from ..base_calculator import TheoryCalculator
from ..base_theory_results import TheoryResults
import numpy as np




class SupernovaTheoryCalculator(TheoryCalculator):
    # This needs to be added by hand for every TheoryCalculator subclass
    name = 'SN'
    statistic_types = ['binned_m']

    def apply_output_systematics(self, c_ell_pair):
        pass

    def run(self, cosmo, parameters, results):
        print("Running SN theory prediction")

        
        ccl.distance_modulus(cosmo, )

        results.set(stat_name, result)
