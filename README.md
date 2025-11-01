# Project02_46W38
Turbie is a simple, two-degree-of-freedom (2DOF) system based of the DTU 10 MW Reference Wind Turbine.

<img src="figures/turbie.png" alt="Turbie Diagram" width="300"/>
<img src="figures/turbie_2DOF_mass_spring_damper.png" alt="Turbie 2DOF mass-spring-damper" width="500"/>

# Discussion
Your task for this project is to build a Turbie module within Python housing the equations required to simulate the system. Then, you can import the module and its functions into another Python script. You will then apply the provided wind files to the model to determine how the blade and tower deflections vary with the wind speed and turbulence itensity (TI).

The functions within the Turbie module should enable the:
* Importing of the wind file data;
* Determination of the $C_T$ for each **wind speed simulation** based on the **average wind speed**, via interpolation with the wind speed vs. $C_T$ look-up table found in C_T.txt;
* Building of the Turbie system matrices ($\mathbf{M}$, $\mathbf{K}$ and $\mathbf{C}$) based on the values within the turbie_parameters.txt;
* Calculation of $\bar{y}'(t)$.

Within your second Python script, you should call upon these functions to solve Turbie for each wind speed case. You should pass $\bar{y}'(t)$ as one of the arguments to the `scipy.integrate.solve_ivp` function (along with initial conditions for $y$), which should then output the blade and tower displacements and velocities of Turbie at each time step.

Your code should enable the simulation of Turbie at each wind speed case within each TI category, with results saved within a text file for each case. 

- For one of the wind speed cases, plot the relative time-marching variation of wind and the blade and tower displacements.

The means and standard deviations of the blade and tower displacements for each wind speed should then be calculated and saved within a separate text file for each TI category.

- Plot the means and standard deviations of the blade and tower displacements for the wind speeds of each TI category.

- Discuss and explain how the means and standard deviations of the blade and tower displacements change with the wind speed and with the TI. 
