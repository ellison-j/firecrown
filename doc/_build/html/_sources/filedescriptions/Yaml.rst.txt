==============
The Yaml File
==============

The Yaml file is the central file for TJPCosmo. The Yaml file needs to be specified in the call to TJPCosmo:

Example::

	Python3 bin/tjpcosmo test/example.yaml


see for example test/3x2pt.yaml

The structure of the Yaml file:
The Yaml file is build up in sections, but before you need to specify  correlated probes::

	correlated_probes: [twopoint]

Sections:
=========

Sampling:
---------

First section is to select witch sampler to use.

This is done by specifying the name of the sampler, the details of the grid, the test, the maximum likelihood details and the fisher matrix if it exists.::

    sampler: test
    grid:
        nsample_dimension: 20
    test:
        fatal_errors: T
        save_dir: 3x2pt
    maxlike:
        maxiter: 1000
        tolerance: 0.01
        output_ini: best.ini
    fisher : {}


Output:
-------
Specify the file for the output

Parameters:
-----------
In this section you specify the parameters used, this includes all cosmological parameters, along with bias parameters, and intrinsic alignment parameters.::

    cosmological_parameters:
        Omega_k: 0.0
        Omega_c:  0.27
        Omega_b: 0.045
        h: 0.67
        n_s: 0.96
        #A_s: 2.1e-9
        sigma_8: 0.8
    linear_bias_lowz:
        b: [3.1, 3.141592653589793, 3.2]
        # test using the default values for these:
        # z_piv: 0.5
        alphaz: 0.0
        alphag: 0.0

    linear_bias_highz:
        b: -666.6  # not currently used
        z_piv: 0.0
        alphaz: 0.0

    linear_ia:
        biasia: 0.03141592653589793
        # fred: 0.5

    wl_pz_shift:
        delta_z:  [0.0, 0.05, 0.1]

    multiplicative_shear_bias:
        m: 0.0

Cosmology systematics:
----------------------
Any systematics for just the cosmology part. These are shared across probes. ::

    baryons:
        type: BaryonEffects
        kmin: 1000

The Probe:
----------
Next specify the details of one probe. First you need to specify the data and likelihood. This means specifying the name and location of the data to run, this is assumed to be in the form of a .sacc file. The likelihood means deciding the type of likelihood, the choices are:

INSERT LIST OF LIKELIHOOD FUNCTIONS WE HAVE IMPLEMENTED (For now just gaussian)

And the covariance correction, by deciding its type and how many realizations.::

    data:
        filename: test/sims/c_ell_mean.sacc
    likelihood:
        type: gaussian
        cov_correction:
            type: Hartlap
            realizations: 100

Next the sources is specified, one probe can have several sources, each source must be given a name, and a type, plus which source systematics that attach to it. 

LIST IMPLEMENTED SOURCES AND SYSTEMATICS. ::

    sources:
        lenses_0:
            type: LSS
            systematics: [linear_bias_lowz, wl_pz_shift] 
        lenses_1:
            type: LSS
            systematics: [linear_bias_lowz, wl_pz_shift]
        lenses_2:
            type: LSS
            systematics: [linear_bias_highz, wl_pz_shift]
        sources_2:
            type: WL
            systematics: [multiplicative_shear_bias,linear_ia, wl_pz_shift]

Next the list of statistics that the probe have to calculate must be given. These are specified by a name, which then have a type, a list of sources and x_min, an x_max, and a list of which probe specific systematics that the probe have.

INSERT LIST OF STATISTICS TYPES ::

    statistics:
        cl_1_1:
            type: ClGG
            source_names: [lenses_1, lenses_1]
            x_min: 8.0
            x_max: 1000.0
            systematics: [additive_shear]
        cl_1_2:
            type: ClGE
            source_names: [lenses_1, sources_2]
            x_min: 8.0
            x_max: 1000.0
            systematics: [additive_shear]
        cl_2_2:
            type: ClEE
            source_names: [sources_2, sources_2]
            x_min: 8.0
            x_max: 1000.0
            systematics: [additive_shear]

Finally a probe also needs a list of the systematics attached, this list is simply to tell TJPCosmo what type of systematic each named systematic for the probe is. So the list is just the name of the systematic and it’s type::

    systematics:
        linear_ia:
            type: LinearAlignment
        linear_bias_lowz:
            type: LinearBias
        linear_bias_highz:
            type: LinearBias
        wl_pz_shift:
            type: PZShift
        multiplicative_shear_bias:
            type: MultiplicativeShearBias
        additive_shear:
            type: AdditiveShearBias
