# -*- coding: utf-8 -*-
import sys
import math
import cmath


try:
    import pylab
    pylab_available = "YES"
except:
    pylab_available = "NO"


####### PROGRAM DESCRIPTION ###########################
#
### CRest_relax_interactive.py ###
# written by Robinson Peric 
# at Hamburg University of Technology (TUHH) and Fakultet Strojarstva i Brodogradnje, Sveučilište u Zagrebu
# version: 26 june 2018
#
### What the code does ###
# The code computes analytical predictions for the reflection coefficient
# for long-crested free-surface wave propagation when using 
# relaxation zones as described in [2]. It is an extension of the theory from [1] for forcing zones; if you are using forcing zones, use the following code:  https://github.com/wave-absorbing-layers/absorbing-layer-for-free-surface-waves
# See [2] for a detailed description how to distinguish between relaxation zones and forcing zones. 
#
### Please note ###
# Recommendations are given in [2] how to tune the relaxation zones parameters depending on the waves. See also the manual distributed along with the code.
# Although theory predictions are often quite accurate [2], please keep in mind that every theory has its limitations! Tuning the absorbing layer parameters according to the present theory does NOT guarantee that the actual reflection coefficient in the simulation will equal the prediction. Other mechanisms can also lead to undesired wave reflections. Thus it is recommended to select layer thickness slightly larger than minimum necessary.
# Future research is necessary to verify how accurate the theory predicts the  damping  of  three-dimensional  waves,  irregular  waves  and  highly  non- linear waves, such as rogue waves, waves close to breaking steepness and even breaking waves; literature results are promising that the theory covers these cases as well.
# 
#
### Reference ###
# [1] Perić, R., & Abdel-Maksoud, M. 2018a. Analytical prediction of reflection coefficients for wave absorbing layers in flow simulations of regular free-surface waves. Ocean Engineering, 147, 132-147.
# [2] Perić, R., Vukčević, V., Abdel-Maksoud, M., Jasak, H. 2018b. Tuning the Case-Dependent Parameters of Relaxation Zones for Flow Simulations With Strongly Reflecting Bodies in Free-Surface Waves. ArXiV preprint, link: 
#
### How to use the program ###
# Call program like this:
# python ./CRestRelax.py
#
#
### Requirements ###
# The programming language python version 2.7 or >=3.0  (https://www.python.org/downloads/) must be installed. 
# It is recommended to also have matplotlib (https://matplotlib.org/users/installing.html) installed. Then the code will plot results beautifully.
#
# Please report errors to robinson.peric@tuhh.de
# 
#####################################################



####### PLOT RESOLUTION and CALCULATION SPEED
factor =1.05					# resolution of plot: very fine & slow (1.01), very coarse & fast (2.0)



####### ENTER USER ARGUMENTS ###########################

foo = input("\n\n\nPlease enter wave period (s):\n")
T = float(foo)

foo = input("\nPlease enter wavelength (m):\n")
L = float(foo)

foo = input("\nPlease enter layer thickness per wavelength (enter 2 if thickness = 2 * wavelength):\n")
layerThickness = L*float(foo)
print("\nAvailable blending functions are:")
print("Power blending [b(x)=x**n]: 1")
print("Cosine**2 blending [b(x)=(cos(x)**2)**n]: 2")
print("Exponential blending [b(x)=(e**(x**n)-1)/(e**1-1)]: 3")
print("Default setting Naval Hydro Pack is: exp")
foo = input("\nPlease enter number of blending function:\n")
blend = str(foo)

foo = input("\nPlease enter power n:\n")
n = float(foo)

# When forcing is applied in all governing eqautions (volume fraction + velocities u,v,w), then the following factor must be 0.25
correction4tau = 0.25

### default settings
csv_file_separator = " "			# alt. "," or ";"
tauMin=10**-4/T*correction4tau	# range of forcing strength tau for which reflection coefficient is computed
tauMax=10**7/T*correction4tau	# -"-
dampres=200							# number of piece-wise constant blending zones, into which absorbing layer is subdivided
Lx = 2.0*L 							# for plots: domain size outside the absorbing layer







###### VARIABLE DECLARATIONS AND INITIALIZATIONS ###########################

# calculate wave parameters 
omega = 2 * math.pi / T
wavenumber_k = 2 * math.pi / L
c = L / T	# phase velocity

# initialize vectors
xd = [0.0] * ( int(dampres) + 2 )		 	# initialize vector for thicknesses of layers, xd[1] is Lx
k = [0.0] * ( int(dampres) + 2 )		 	# initialize vector for wave number, k[1] is 2*pi/L
Ct = [0.0] * ( int(dampres) + 2 )		 	# initialize vector for transmission coefficient, Ct[1] is coefficient for entrance to absorbing layer
beta = [0.0] * ( int(dampres) + 2 )			# initialize vector needed to compute Cr
Cr = [0.0] * ( int(dampres) + 2 )		 	# initialize vector for reflection coefficient, Cr[1] is the global reflection coefficient (i.e. for the entrance to the absorbing layer)

# write initial conditions
dx = layerThickness / dampres	# thickness of single 'cell' within damping layer
xd[1] = Lx
for i in range(2,dampres+2,1):
	xd[i] = dx
k[0] = wavenumber_k
k[1] = wavenumber_k
Ct[0] = 1.0
Cr[0] = 0.0
Ct[dampres+1] = 0.0
Cr[dampres+1] = 1.0




###### FUNCTION DECLARATIONS ###########################

def abs(x):
	return math.sqrt( (x.real)**2 + (x.imag)**2 )	# return absolute value of complex number x




# evaluate blending function
def b(x):
	if (x >= Lx):
		# power
		if (blend == "1"):
			w = ( ( x - Lx ) / ( ( Lx + layerThickness ) - Lx ) )**n  # Eq. (7) in [2]

		# cosine-squared
		elif (blend == "2"):
			w = ( (math.cos( 0.5 * math.pi + 0.5 * math.pi * ( x - Lx ) / ( ( Lx + layerThickness ) - Lx ) )**2)**n )  # Eq. (6) in [2]
			

		# exponential
		elif (blend == "3"):
			w = ( (math.exp( ( ( x - Lx ) / ( ( Lx + layerThickness ) - Lx )  )**n ) -1) / ( math.exp(1) - 1 ) )  # Eq. (5) in [2]

		#--- uncomment and enter custom blending function here ---
		#elif (blend == "4"):
		#	w = ?

		else:
			print("ERROR: Specified blending function not found.")
			sys.exit(1)
		
		return ( w / ( tau**2 * ( 1.0 - w ) ) )		# division by "tau**2" since in later equations multiplication by "tau" occurs (i.e. this is effectively "w / (tau * (1 - w))")
	
	else:
		return 0.0

def fbeta(i):
    return ( ( 1.0 + Cr[i] * cmath.exp( 1j * k[i] * xd[i] * 2.0 )  ) / ( 1.0 -  Cr[i] * cmath.exp( 1j * k[i] * xd[i] * 2.0 ) ) )

def fCt(i):
    return ( 1.0 - Cr[i] ) / (  1.0 - Cr[i+1] * cmath.exp( 1j * k[i+1] * xd[i+1] * 2.0 )  ) 

def fCr(i):
    return ( -k[i] + k[i+1] * beta[i+1] ) / ( k[i] + k[i+1] * beta[i+1] )






###### MAIN ##############################################
tau = tauMin
G=[]
CR=[]

# create file
f = open("C_R.csv", 'w')
f.close()

# calculate C_R for different tau values
while (tau < tauMax):
	tmp = Lx
	for i in range(2,dampres+2,1):
		k[i] = cmath.sqrt(  (omega**2)/ ( c**2 ) + (1j * omega * tau * b( tmp + 0.5 * xd[i] ) ) / ( (c)**2 ))
		tmp += xd[i]

	# calculate transmission and reflection coefficients
	for i in range(dampres,0,-1):   #go cell-by-cell from end of the layer to layer entrance. E.g. for 3 zones, start with zone 3, then 2, then 1.
		beta[i+1] = fbeta(i+1)
		Cr[i] = fCr(i)
		Ct[i] = fCt(i)

	# write reflection coefficients to file
	f = open("C_R.csv", 'a')
	f.write(str(tau/correction4tau) + csv_file_separator + str(abs(Cr[1])) +  "\n")
	G.append(tau/correction4tau)
	CR.append(abs(Cr[1]))
	f.close()

	tau = tau * factor


# if pylab and matplotlib are installed, open window and plot C_R(tau)
if (pylab_available == "YES"):
	pylab.figure(figsize=(20,8))
	pylab.xlabel('$\\tau \ (\mathrm{s})$ ', {'fontsize': 20})
	pylab.ylabel('$C_R$', {'fontsize': 20})
	pylab.semilogx()
	pylab.semilogy()
	pylab.plot(G,CR, linewidth=1.5)
	pylab.show()

print("\n\nProgram finished. \nReflection coefficients were written to file C_R.csv\n")

sys.exit(0)

