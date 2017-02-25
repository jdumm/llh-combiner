import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import pickle


# Just a stub for playing around with splines.

#This function is now just for testing by setting data to one example.
def nextxyg():
	# The bin info will give the start
	g = [0,3,31]
	#g = [0,0.7,8]

	# List of bin edges, including the max:
	x = np.linspace(g[0],g[1],g[2])
	y = [-0.00e+00,1.00e+00,1.83e+00,2.51e+00,3.07e+00,3.53e+00,3.89e+00,4.17e+00,4.37e+00,4.50e+00,4.57e+00,4.58e+00,4.53e+00,4.42e+00,4.27e+00,4.06e+00,3.80e+00,3.50e+00,3.16e+00,2.77e+00,2.33e+00,1.86e+00,1.35e+00,7.95e-01,2.04e-01,-4.24e-01,-1.09e+00,-1.79e+00,-2.53e+00,-3.30e+00,-4.5e+00]
	#y = [-0.00e+00,1.00e+00,1.83e+00,2.51e+00,3.07e+00,3.53e+00,3.89e+00,4.17e+00]
	return x,y,g

def calcchi2(x,y,spl):
	chi2 = float(0)
	for i in range(len(x)):
		chi2 += pow(spl(x[i]) - y[i],2)
	#chi2 /= len(x)
	return chi2 

spls = []
for i in range(1):
	x,y,g = nextxyg()

	#spl = UnivariateSpline(x,y)
	#spl = UnivariateSpline(x, y, k=2, s=0.5)
	spl = UnivariateSpline(x, y, s=0.15)
	xs = np.linspace(g[0]-1, g[1]+1, 100*(g[2]+1))
	maxi = spl(xs).max()
	print('chi2 = {}, max = {}'.format(calcchi2(x,y,spl),maxi))
	spls.append(spl)

plt.plot(x, y, 'ro', ms=5)
plt.plot(xs, spl(xs), 'g', lw=3)
#spl.set_smoothing_factor(0.5)
#plt.plot(xs, spl(xs), 'b', lw=3)
plt.show()


ofile = open('testout.pkl','wb')
pickle.dump(spls,ofile)
ofile.close()

