#%%
from turbie_mod import *
import matplotlib.pyplot as plt

#%%
# read the wind file
pathfile_wind = r"inputs\wind_files\wind_TI_0.1\wind_4_ms_TI_0.1.txt"
t, wsp = read_wind_txt(pathfile_wind)

# estimate the cts as f(wsp)
ct = get_ct(wsp)

# create M, C, K matrices
M, C, K, params = get_MCK()

# %%

# %%
