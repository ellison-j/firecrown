import numpy as np
import pandas as pd
import pyccl as ccl

from ..core import Statistic


def _ell_for_xi(ell_min=2, ell_mid=50, ell_max=6e4, n_log=200):
    """Build an array of ells to sample the power spectrum for real-space
    predictions.
    """
    return np.concatenate((
        np.linspace(ell_min, ell_mid-1, ell_mid-ell_min),
        np.logspace(np.log10(ell_mid), np.log10(ell_max), n_log)))


class TwoPointStatistic(Statistic):
    """A two-point statistic (e.g., shear correlation function, galaxy-shear
    correlation function, etc.).

    Parameters
    ----------
    data : str
        The path to a CSV file with the measured statistic. The columns should
        either be {'t', 'xi'} or {'l', 'cl'}.
    kind : str
        The kind of two-point statistic. One of
            - 'cl' : angular power spectrum
            - 'gg' : angular position auto-correlation function
            - 'gl' : angular cross-correlation between position and shear
            - 'l+' : angular shear auto-correlation function (xi+)
            - 'l-' : angular shear auto-correlation function (xi-)
    sources : list of str
        A list of the sources needed to compute this statistic.
    systematics : list of str, optional
        A list of the statistics-level systematics to apply to the statistic.
        The default of `None` implies no systematics.
    ell_min : int
        The minimum angulare wavenumber to use for real-space integrations.
    ell_mid : int
        The midpoint angular wavenumber to use for real-space integrations. The
        angular wavenumber samples are linearly spaced at integers between
        `ell_min` and `ell_mid`.
    ell_max : float
        The maximum angular wavenumber to use for real-space integrations. The
        angular wavenumber samples are logarithmically spaced between
        `ell_mid` and `ell_max`.
    n_log : int
        The number of logarithmically spaced angular wavenumber samples between
        `ell_mid` and `ell_max`.

    Attributes
    ----------
    ell_or_theta_ : np.ndarray
        The final array of ell/theta values for the statistic. Set after
        `compute` is called.
    measured_statistic_ : np.ndarray
        The measured value for the statistic.
    predicted_statistic_ : np.ndarray
        The final prediction for the statistic. Set after `compute` is called.
    scale_ : float
        The final scale factor applied to the statistic. Set after `compute`
        is called. Note that this scale factor is already applied.
    """
    def __init__(self, data, kind, sources, systematics=None,
                 ell_min=2, ell_mid=50, ell_max=6e4, n_log=200):
        self.data = data
        self.kind = kind
        df = pd.read_csv(self.data)
        if self.kind == 'cl':
            self._ell_or_theta = df['l'].values.copy()
            self._stat = df['cl'].values.copy()
        else:
            self._ell_or_theta = df['t'].values.copy()
            self._stat = df['xi'].values.copy()
        self.sources = sources
        self.systematics = systematics or []
        self.ell_min = ell_min
        self.ell_max = ell_max
        self.ell_mid = ell_mid
        self.n_log = n_log

    def compute(self, cosmo, params, sources, systematics=None):
        """Compute a two-point statistic from sources.

        Parameters
        ----------
        cosmo : pyccl.Cosmology
            A pyccl.Cosmology object.
        params : dict
            A dictionary mapping parameter names to their current values.
        sources : dict
            A dictionary mapping sources to their objects. The sources must
            already have been rendered by calling `render` on them.
        systematics : dict, optional
            A dictionary mapping systematic names to their objects. The
            default of `None` corresponds to no systematics.
        """
        self.ell_or_theta_ = self._ell_or_theta.copy()
        self.measured_statistic_ = self._stat.copy()

        tracers = [sources[k].tracer_ for k in self.sources]
        self.scale_ = np.prod([sources[k].scale_ for k in self.sources])

        if self.kind == 'cl':
            self.predicted_statistic_ = ccl.angular_cl(
                cosmo, *tracers, self.ell_or_theta_) * self.scale_
        else:
            ells = _ell_for_xi(
                ell_min=self.ell_min,
                ell_mid=self.ell_mid,
                ell_max=self.ell_max,
                n_log=self.n_log)
            cells = ccl.angular_cl(cosmo, *tracers, ells)
            self.predicted_statistic_ = ccl.correlation(
                cosmo, ells, cells, self.ell_or_theta_ / 60,
                corr_type=self.kind) * self.scale_

        systematics = systematics or {}
        for systematic in self.systematics:
            systematics[systematic].apply(cosmo, params, self)
