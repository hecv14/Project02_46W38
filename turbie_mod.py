#%% IMPORTS
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

#%% import wind file data

#%% determine Ct

# read Ct table for the WTG rotor
def read_wsp_ct_tbl(
        ct_filepath: str = r"inputs\turbie_inputs\CT.txt"
        ) -> np.ndarray:
    """reads CT.txt containing Ct as f(wsp)

    Args:
        ct_filepath (str, optional): path to CT.txt.
        
    Returns:
        np.ndarray: parsed Wsp and Ct columns
    """    
    # NOTE: np.loadtxt is faster for numeric well-structured files
    wsp_ct_tbl = np.loadtxt(ct_filepath, skiprows=1)
    return wsp_ct_tbl
    # # using "with open"
    # wsp = []; ct = []
    # with open(ct_filepath, 'r', encoding='utf-8') as f:
    #     next(f) # skips header line
    #     for line in f: # read line by line
    #         line = line.strip() # remove whitespace
    #         cols = line.split() # list of substrings
    #         wsp.append(float(cols[0]))
    #         ct.append(float(cols[1]))
    # wsp_ct_tbl = np.array([wsp,ct]).T
    # return wsp_ct_tbl


def get_ct(wsp, wsp_ct_tbl):
    # extract x and y and create interpolation model
    tbl_wsp = wsp_ct_tbl[:,0]
    tbl_ct = wsp_ct_tbl[:,1]
    f_linear = interp1d(tbl_wsp, tbl_ct, kind="linear")
    # interpolate
    ct = f_linear(wsp)
    #plt.plot(tbl_wsp, tbl_ct); plt.scatter(wsp, ct)
    return ct


#%% build system matrices M, K and C


#%% calculate y(t)
