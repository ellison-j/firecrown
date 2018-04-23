from .base_systematic import SourceSystematic, OutputSystematic, CosmologySystematic
import pyccl as ccl


class MassObservableRelation1(SourceSystematic):
    params = ['m']
    def adjust_source(self, cosmo, source):
        pass
