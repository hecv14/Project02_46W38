#%% IMPORTS
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

#%% CUSTOM Fs

def read_simple_txt(filepath):
    """read numeric text files skipping header in first line

    Args:
        filepath (str): location of .txt

    Returns:
        array_from_txt (np.array): array with numeric content of the .txt
    """
    # read txt skipping header in first row
    array_from_txt = np.loadtxt(filepath, skiprows=1)
    # NOTE: np.loadtxt works well only because of the well-structured numeric
    # project files, for a more ambitious project #with open()# and adequate
    # error handling would be required.
    return array_from_txt


# Import wind data
def read_wind_txt(filepath_wind):
    """import wind data and store t and wsp an numpy arrays

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


# Determine ct as f(wsp, and Ct table)
def get_ct(wsp, filepath_ct=r"inputs\turbie_inputs\CT.txt"):
    """get ct coefficients from interpolation of a Wsp-Ct table; if no wsp is
    passed the interpolation class will be returned instead

    Args:
        wsp (np.array): arbitrary wind speed for which the ct must be determined
        filepath_ct (optional): location of CT.txt file with ct as f(wsp)

    Returns:
        ct (np.array): ct interpolated for input wsp or interpolation class
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
    if wsp != None:
        # get Ct
        ct = f_linear(wsp)
        return ct
    else:
        # return only the interpolation class
        return f_linear


# Import Turbie parameters
def get_turbie_params(
        filepath_params=r"inputs\turbie_inputs\turbie_parameters.txt"
        ):
    """read turbie_parameters.txt and store in dict. Adds rotor area parameter.

    Args:
        filepath_params (str, optional): path to the turbie_parameters.txt
    """
    params = {} # instantiate empty dict
    with open(filepath_params, 'r', encoding='utf-8') as f:
        next(f) # skip header
        for line in f: # read line by line
            line = line.strip() # remove whitespace
            col = line.split() # list of substrings
            # col[2] holds the name, col[0] the value
            params[f'{col[2]}'] = float(col[0]) # create key-value pair in dict
        # add Ar (Area of the rotor)
        params['Ar'] = np.pi/4 * params['Dr']**2
    return params


# build Turbie system matrices
def get_MCK(params: dict): 
    """build system matrices M, K and C based on turbie_parameters dictionary

    Args:
        params (dict): parameters dict created with read_turbie_params()

    Returns:
        M (np.array): M matrix
        C (np.array): C matrix
        K (np.array): K matrix
    """
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
    return M, C, K


# Calculate dy
def dy(t, y, M, C, K, wind_t, wind_wsp, rotor_area, ct, rho):
    """Function of the rate of change for Turbie's 2-DOF system

    Args:
        t (float): Current time (s)
        y (array_like): Current values of the dependent variables
        M (np.array): Mass Matrix
        C (np.array): Damping Matrix
        K (np.array): Stiffness Matrix
        wind_t (np.array): Forcing wind speed time (s)
        wind_wsp (np.array): Forcing wind speed (m/s)
        rotor_area (float): Rotor area (m²)
        ct (float): Thrust coefficient, ct (-)
        rho (float, optional): Air density (kg/m³)

    Returns:
        dy (np.array): The derivative at time `t` of `y`.
    """
    # state vector:
    x1, x2, dx1, dx2 = y

    # wind_t is not necessarily = t! interpolation required
    # create interpolation class
    f_linear = interp1d(wind_t,
                        wind_wsp,
                        kind="linear",
                        fill_value="extrapolate")
    u_t = f_linear(t) # wind speed at time t

    # Forcing 
    u_rel = (u_t - dx1)
    # Thrust: acts only on blades (m1)   
    f1_t = 0.5 * rho * ct * rotor_area * u_rel * abs(u_rel) 
    # no force on m2   
    f2_t = 0
    F_t = np.array([f1_t, f2_t])

    # state and derivative vectors
    x = np.array([x1, x2])
    dx = np.array([dx1, dx2])

    # invert M
    Minv = np.linalg.inv(M)

    # solving for ddx from: M * ddx + C * dx + K * x = F_t    
    ddx = Minv @ (F_t - C @ dx - K @ x)

    # build state matrix
    N = 2 # dof
    Z = np.zeros((N, N))
    I = np.eye(N)
    A = np.block([[Z, I], [-Minv @ K, -Minv @ C]])    
    # build input matrix
    B = np.concatenate((np.zeros(N), Minv @ F_t))

    # derivative of state vector
    dy = A @ y + B
    return dy


# run a Turbie simulation with solve_ivp
def simulate_turbie(t_span, t_eval, args, y0=[0, 0, 0, 0]):
    """use solve_ivp to solve Turbie's 2-DOF equations

    Args:
        t_span (tupple): time span to solve
        y0 (list, optional): Initial (t=0), x1, x2, dx1, dx2. Defaults all to 0.
        t_step (float, optional): time step for t_eval. Defaults to 0.01 s.
    """
    # f args NOTE: will fail if args dont exist in scope!
    #args = (M, C, K, wind_t, wind_wsp, params['Ar'], ct, params['rho'])        
    # Solve the ODE (fy must exist in scope!)
    sol = solve_ivp(dy, t_span=t_span, y0=y0, t_eval=t_eval, args=args)
    return sol.t, sol.y[0], sol.y[1], sol.y[2], sol.y[3]
    
# %%
