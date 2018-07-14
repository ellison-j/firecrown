"""
TJPCosmo wrapper for FASTPT, to call CCL for Pk, return relevant FASTPT quantities.
"""
import numpy as np
from scipy.interpolate import interp1d

import FASTPT
from FASTPT.info import __version__

#Version check
version_major_needed = 2

print('This is FAST-PT version', __version__)
version_major = int(float(__version__))

### Do a version check ###
assert version_major == version_major_needed,'TJPCosmo requires FASTPT v2.X'

#####

# Get to_do list for FASTPT from the relevant analysis object attribute
# which has been populated by parsing the YAML file for source systematics
fastpt_to_do = two_point.fastpt
# Note, FASTPTv2 uses a to_do list. v1 does not. We hope to re-write code for v3 to remove need for to-do list.


######
# get k and Plin grid from CCL. Use z=0. CCL will do the growth calculation downstream.
# We eventually want to separate out the k step so it can be done only once

# CCL call to get power spectrum

k_CCL = 
Plin_CCL = 

# check for log spacing
# broadcast onto a log spaced grid if necessary

dk=np.diff(np.log(k_CCL))
delta_L=(log(k_CCL[-1])-log(k_CCL[0]))/(k_CCL.size-1)
dk_test=np.ones_like(dk)*delta_L
		
try:
    log_sample_test='FASTPT requires log spaced k values. Creating log-spaced k array now.'
    np.testing.assert_array_almost_equal(dk, dk_test, decimal=4, err_msg=log_sample_test, verbose=False)
    # how should this be handled? Does it return TRUE/FALSE?
except AssertionError:
    nk = 4*len(k_CCL) # resolution should be optimized or we should allow it to be specified. Higher res increasese runtime.
    k = np.logspace(k_CCL[0], k_CCL[-1], nk)
    klog=np.log(k)
    Plininterp = interp1d(np.log(k_CCL), np.log(Plin_CCL))
    Plin = np.exp(Plininterp(klog))
    
# change resolution even for input log spaced k grid?

# extend to high and low k. This can be done internally in FASTPT or separately.
# Separating the extension step may help if we initialize the k grid a single time.

# right now, done within FASTPT. See below.

####

# Call FASTPT to initialize k grid quantities.
# This could be done once at the beginning of a chain, if the k grid remains fixed.
n_pad = len(k)
fastpt = FASTPT.FASTPT(k, to_do=fastpt_to_do, low_extrap=-5, high_extrap=3, n_pad=n_pad)


# Call specific quantities 
# this will need to be updated if we move away from the to_do list API

C_window=.75 # this could be optimized or made an option

if fastpt.dd_do:
    if fastpt.dd_bias_do:
        P_one_loop_dd = fastpt.one_loop_dd(P,C_window=C_window)
    else:
        P_one_loop_dd_bias = fastpt.one_loop_dd_bias(P,C_window=C_window)

if fastpt.IA_tt_do:
    P_IA_tt=fastpt.IA_tt(P,C_window=C_window)

if fastpt.IA_ta_do:
    P_IA_ta=fastpt.IA_ta(P,C_window=C_window)

if fastpt.IA_mix_do:
    P_IA_mix=fastpt.IA_mix(P,C_window=C_window)

if fastpt.RSD_do:
    P_RSD=fastpt.RSD_components(P,1.0,C_window=C_window)

sig4=fastpt.sig4(P,C_window=C_window)
