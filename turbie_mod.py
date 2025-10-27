#%% IMPORTS
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

#%% read the project well-structured numeric files
def read_simple_txt(filepath):
    """read numeric text files skipping header in first line

    Args:
        filepath (str): location of .txt

    Returns:
        array_from_txt (np.array): array with numeric content of the .txt
    """
    # read txt skipping header in first row
    array_from_txt = np.loadtxt(filepath, skiprows=1)
    return array_from_txt


def read_wind_txt(filepath_wind):
    """read wind files

    Args:
        filepath_wind (str): location of

    Returns:
        t (np.array): time (s)
        wsp (np.array): wind speed (m/s)
    """
    # rely on read_simple_txt
    wind_txt = read_simple_txt(filepath_wind)
    # identify the t and wsp
    t = wind_txt[:,0]
    wsp = wind_txt[:,1]
    return t, wsp


def get_ct(wsp, filepath_ct=r"inputs\turbie_inputs\CT.txt"):
    """get ct coefficients for an arbitrary wind speed using existing CT table

    Args:
        wsp (np.array): arbitrary wind speed for which the ct must be determined
        filepath_ct (optional): location of CT.txt file with ct as f(wsp)

    Returns:
        ct (np.array): ct interpolated for input wsp
    """
    # read Ct table for the WTG rotor
    tbl_wsp_ct = read_simple_txt(filepath_ct)
    tbl_wsp = tbl_wsp_ct[:,0]
    tbl_ct = tbl_wsp_ct[:,1]
    # create interpolation class
    f_linear = interp1d(tbl_wsp,
                        tbl_ct,
                        kind="linear",
                        fill_value="extrapolate")
    # get Ct
    ct = f_linear(wsp)
    return ct


def get_MCK(
        filepath_params: str = r"inputs\turbie_inputs\turbie_parameters.txt"
        ): 
    """build system matrices M, K and C based on turbie_parameters.txt

    Args:
        filepath_params (str, optional): path to the turbie_parameters.txt

    Returns:
        M (np.array): M matrix
        C (np.array): C matrix
        K (np.array): K matrix
        params (dict): parameter names and values
    """
    params = {} # instantiate empty dict
    with open(filepath_params, 'r', encoding='utf-8') as f:
        next(f) # skip header
        for line in f: # read line by line
            line = line.strip() # remove whitespace
            col = line.split() # list of substrings
            # col[2] holds the name, col[0] the value
            params[f'{col[2]}'] = float(col[0]) # create key-value pair in dict

    # Mass 1 represents the 3 blades
    m1 = 3 * params['mb']
    # Mass 2 represents the combined effects of the nacelle, hub and tower.
    m2 = params['mn'] + params['mh'] + params['mt']
    # create the mass, damping and stiffness matrices
    M = np.diag([m1, m2])
    C = np.array([
        [params['c1'],-params['c1']],
        [-params['c1'],params['c1']+params['c2']]
        ])
    K = np.array([
        [params['k1'],-params['k1']],
        [-params['k1'],params['k1']+params['k2']]
        ])    
    return M, C, K, params


#%% calculate y(t)
#def dydt(t, y, M, C, K, A, rho, ct, wind):

