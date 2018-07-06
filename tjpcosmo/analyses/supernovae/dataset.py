from ...dataset import BaseDataSet
import numpy as np

class SupernovaDataSet(BaseDataSet):
    def __init__(self, z, m, dm, sys_covmat):
        self.z = z
        self.m = m
        self.dm = m
        self.sys_covmat = sys_covmat

        self.n = len(z)

        C = np.copy(sys_covmat)
        for i in range(n):
            C[i,i] += dm**2



    @classmethod
    def load(cls, filename, config):
        import h5py
        f = h5py.File(filename, mode='r')
        z = f['sn_data/zcmb'][:]
        m = f['sn_data/mb'][:]
        dm = f['sn_data/dmb'][:]
        sys_covmat = f['covariances/total'][:]
        return cls(z, m, dm, sys_covmat)
    
