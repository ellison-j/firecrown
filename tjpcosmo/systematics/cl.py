from .base_systematic import (
    SourceSystematic, OutputSystematic, CosmologySystematic)
import pyccl as ccl


class MORPowerLaw(SourceSystematic):
    """The mass-observable relation (MOR) systematic. This class assumes
    a power law for the MOR.
    
    """
    params = ['slope','intercept','scatter']

    """
    def adjust_source(self, cosmo, source):
        #""Adjust the source by modifying it according to 
        the MOR TODO: implement this
        #""
        if self.adjust_requirements(source):
            return 0
        else:
            print(
                f"{self.__class__.__name__} did not find all "
                "required source parameters")
            return 1
        """
    pass

class BoostFactorProfile(SourceSystematic):
    """Adjust the cluster lensing profile by computing the
    boost factor model and de-boosting the lensing profile.
    
    Note: params all have to be lower case.

    """
    params = ['r_scale', 'b0']
    #def adjust_source(self, cosmo, source):
    pass
