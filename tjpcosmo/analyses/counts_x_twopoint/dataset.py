from ...dataset import BaseDataSet
import sacc
import numpy as np


class CountsXTwoPointDataSet(BaseDataSet):
    def __init__(self, sacc_data, indices):
        """Create a data set for counts X 2pt statistics.

        Args:
            sacc_data (:obj:`sacc`): Save all correlations and 
                covariances object
            indices (:obj:`list`): Indices of the tracers to use that ends 
                up slicing the covariance matrix and data vector tables
        
        """
        self.data_vector = sacc_data.mean.vector[indices]
        self.covariance = sacc_data.precision.cmatrix[indices, :][:, indices]
        # TODO: optimize this through Cholesky
        self.precision = np.linalg.inv(self.covariance)
        self.nsims = sacc_data.meta.get("nsims", 0)

    @classmethod
    def load(cls, filename, config):
        """Create a data set for counts X 2pt statistics from a filename

        Args:
            filename (:obj:`str`): Filename
            config (:obj:?): TODO

        """
        sacc_data = sacc.SACC.loadFromHDF(filename)
        indices, metadata = counts_x_twopoint_process_sacc(sacc_data, config)
        twp = cls(sacc_data, indices)
        return twp, metadata

def counts_x_twopoint_process_sacc(sacc_data, config):
    """Deconstruct the SACC data object.

    Args:
        sacc_data (:obj:`sacc`): Save all correlations and 
            covariances object
            config (:obj:?): TODO

    Returns:
        (:obj:`numpy array`): indices of which columns are to be used
        (:obj:`dict`): Dictionary containing ? TODO

    """
    #Acquire a list of the tracers and how they are combined
    #this is a condensed form of the "binning" field on the SACC
    tracer_sorting = sacc_data.sortTracers()

    metadata = {}
    metadata['sources'] = {}
    #The list of the 1st tracers (can include CL counts)
    t1_list = np.array([s[0] for s in tracer_sorting])
    #The list of the 2nd tracers. For CL_counts, has a -1 index
    t2_list = np.array([s[1] for s in tracer_sorting])
    #Types of individual measurements
    typ_list = np.array([s[2].decode() for s in tracer_sorting])
    xs_list = [s[3] for s in tracer_sorting]  #the 'ells' in the sacc
    ndx_list = [s[4] for s in tracer_sorting] #which ell bins are used

    #Map the tracers to indices
    tracer_numbers = {}
    for itr, tr in enumerate(sacc_data.tracers):
        tracer_numbers[str(eval(tr.name).decode())] = itr

    #Obtain the z and Nz fields from the sacc for each tracer
    for name, d in config['sources'].items():
        t = sacc_data.tracers[tracer_numbers[name]]
        metadata['sources'][name] = {'z': t.z, 'nz': t.Nz}

    
    indices = [] #which indices should be used for the columns in the cov. matrix and
    #data vector.
    pair_ordering = [] #Mislabeled name - was originally the ordering of the 3x2pt
    #probes, but now it includes N counts.
    # Dictionary between SACC cluster+2pt types and TJPCosmo clusters+2pt types
    dict_types = {
        'CL_counts': '+N',
        'gamma_t':   '+R'}
    # Loop over all statistics in the yaml file
    for xcor, d in config['statistics'].items():
        #xcor is the name of the source involved in a statistic
        #d is a dictionary with info on the statistic
        print("xcor = ", xcor)
        #Pick out the numbers of the tracers here
        tns = sorted([tracer_numbers[n] for n in d['source_names']])
        #print(tns)
        #Pick out the types of the tracers here
        typ = dict_types[d['type']]
        #print(typ, d['type'])
        if len(tns) < 2 and len(tns) > 0: #We have a number count
            id_xcor = np.where( (t1_list == tns[0]) & (typ_list == typ))[0]
        elif len(tns) == 2: #a 2pt
            id_xcor = np.where(
                (t1_list == tns[0]) & (t2_list == tns[1]) & (typ_list == typ))[0]
        if len(id_xcor) == 0:
            raise ValueError(
                f"The correlation {xcor} is not present in the SACC file")
        elif len(id_xcor) != 1:
            raise ValueError(
                f"This SACC file is wrong, the correlation "
                f"{xcor} appears more than once")
        else:
            id_xcor = id_xcor[0]          #ID of this measurement
            xs_full = xs_list[id_xcor]    #All of the "x"s, or bins
            ndxs_full = ndx_list[id_xcor] #The indices of the xs to use
            if d['type'] == "CL_counts":
                pair_ordering.append({
                    'name': xcor,
                    'src1': d['source_names'][0],
                    'src2': None,
                    'type': d['type'],
                    'xs': None,
                })
                indices += ndxs_full.tolist()
            else:
                #Incorporate scale cuts
                indices_cut = np.where(
                    (xs_full <= d['x_max']) & (xs_full >= d['x_min']))[0]
                #Append the indices of the proper columns
                indices += ndxs_full[indices_cut].tolist()
                #Record pair information
                pair_ordering.append({
                    'name': xcor,
                    'src1': d['source_names'][0],
                    'src2': d['source_names'][1],
                    'type': d['type'],
                    'xs': xs_full[indices_cut],
                })
    metadata['ordering'] = pair_ordering
    return np.array(indices), metadata
