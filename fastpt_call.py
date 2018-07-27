"""
TJPCosmo wrapper for FASTPT, to call CCL for Pk, return relevant FASTPT quantities.
Credit: Some work on this code was completed at the Aspen Center for Physics
"""
import sys
import numpy as np
from scipy.interpolate import interp1d

import FASTPT.FASTPT as FASTPT
from FASTPT.info import __version__

#Version check
version_major_needed = 2

print('This is FAST-PT version', __version__)
version_major = int(float(__version__))

try:
    assert version_major == version_major_needed,'TJPCosmo requires FASTPT v2.X'
except AssertionError as e:
    raise
    #sys.exit(1)
#####

# Get to_do list for FASTPT from the relevant analysis object attribute
# which has been populated by parsing the YAML file for source systematics
#fastpt_to_do = two_point.fastpt #replace with relevant attribute when available
# Note, FASTPTv2 uses a to_do list. v1 does not. We hope to re-write code for v3 to remove need for to-do list.

#TEMPORARY HACK to test code:
fastpt_to_do = ['dd_bias']


######
# get k and Plin grid from CCL. Use z=0. CCL will do the growth calculation downstream.
# We eventually want to separate out the k step so it can be done only once

# CCL call to get power spectrum

#TEMPORARY HACK to test code
d=np.loadtxt('FASTPT/Pk_test.dat') 
k_CCL = d[:,0]
Plin_CCL = d[:,1]

# check for log spacing
# broadcast onto a log spaced grid if necessary

dk=np.diff(np.log(k_CCL))
delta_L=(np.log(k_CCL[-1])-np.log(k_CCL[0]))/(k_CCL.size-1)
dk_test=np.ones_like(dk)*delta_L
		
try:
    log_sample_test='FASTPT requires log spaced k values. Creating log-spaced k array now.'
    np.testing.assert_array_almost_equal(dk, dk_test, decimal=4, err_msg=log_sample_test, verbose=False)
    k=k_CCL
    P=Plin_CCL
except AssertionError:
    print(log_sample_test)
    nk = 4*len(k_CCL) # resolution should be optimized or we should allow it to be specified. Higher res increasese runtime.
    k = np.logspace(np.log10(k_CCL[0]), np.log10(k_CCL[-1]), nk)
    klog=np.log(k)
    Plininterp = interp1d(np.log(k_CCL), np.log(Plin_CCL), bounds_error=False, fill_value='extrapolate')
    Plin = np.exp(Plininterp(klog))
    P=Plin
    
# OPTIONAL STEPS THAT COULD BE ADDED HERE    
# change resolution even for input log spaced k grid?

# extend to high and low k. This can be done internally in FASTPT or separately.
# Separating the extension step may help if we initialize the k grid a single time.
# right now, done within FASTPT. See below.

####

# Call FASTPT to initialize k grid quantities.
# This could be done once at the beginning of a chain, if the k grid remains fixed.
n_pad = len(k)
fastpt = FASTPT.FASTPT(k, to_do=fastpt_to_do, low_extrap=-5, high_extrap=3, n_pad=n_pad)

# Call FASTPT to generate requested quantities
# this will need to be updated if we move away from the to_do list API

C_window=.75 # this could be optimized or made an option

to_ccl = {}
to_ccl['k'] = k
to_ccl['Plin'] = P
to_ccl['Pnl'] = P # needs to be updated with halofit or other from CCL
#update column numbers
if fastpt.dd_do:
    if fastpt.dd_bias_do:
        P_one_loop_dd = fastpt.one_loop_dd(P,C_window=C_window)
        to_ccl[dd_1loop] = P_one_loop_dd[0]
    else:
        P_one_loop_dd_bias = fastpt.one_loop_dd_bias(P,C_window=C_window)
        to_ccl[dd_1loop] = P_one_loop_dd[0]
        to_ccl[d2d2] = P_one_loop_dd[1]
        

if fastpt.IA_tt_do:
    P_IA_tt=fastpt.IA_tt(P,C_window=C_window)
    to_ccl[ia_tt] = P_IA_tt[0]

if fastpt.IA_ta_do:
    P_IA_ta=fastpt.IA_ta(P,C_window=C_window)
    to_ccl[ia_ta] = P_IA_ta[0]

if fastpt.IA_mix_do:
    P_IA_mix=fastpt.IA_mix(P,C_window=C_window)
    to_ccl[ia_mix] = P_IA_mix[0]

if fastpt.RSD_do:
    P_RSD=fastpt.RSD_components(P,1.0,C_window=C_window)
    to_ccl[rsd] = P_RSD[0]

sig4=fastpt.sig4(P,C_window=C_window)
to_ccl['sig4'] = sig4
#Pass pointer to to_ccl dictionary