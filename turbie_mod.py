#%% IMPORTS
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

#%% read the project well-structured numeric files
def read_simple_txt(filepath: str) -> np.ndarray:
    """read_simple_txt reads the numeric project's wind files

    Args:
        filepath (str): path of the file

    Returns:
        np.ndarray: for wind_files, array with time (s) and wsp (m/s)
    """
    array_from_txt = np.loadtxt(filepath, skiprows=1)
    return array_from_txt


#%% get Ct

# read Ct table for the WTG rotor
def read_wsp_ct_tbl(
        filepath_ct: str = r"inputs\turbie_inputs\CT.txt"
        ) -> np.ndarray:
    """reads CT.txt containing ct as f(wsp)

    Args:
        filepath_ct (str, optional): path to CT.txt.
        
    Returns:
        np.ndarray: parsed wsp and ct columns
    """    
    # NOTE: reusing read_simple_txt
    wsp_ct_tbl = read_simple_txt(filepath_ct)
    return wsp_ct_tbl

def get_ct(wsp: float, wsp_ct_tbl: np.ndarray) -> float:
    """get_ct 1d interpolation for a given wsp using CT.txt

    Args:
        wsp (float): wind speed for which ct is interpolated
        wsp_ct_tbl (np.ndarray): wsp and ct columns

    Returns:
        ct: thrust coefficient (-)
    """
    # extract x and y and create interpolation model
    tbl_wsp = wsp_ct_tbl[:,0]
    tbl_ct = wsp_ct_tbl[:,1]
    f_linear = interp1d(tbl_wsp, tbl_ct, kind="linear")
    # interpolate
    ct = f_linear(wsp)
    return ct


#%% build system matrices M, K and C


#%% calculate y(t)
