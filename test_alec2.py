import autograd.numpy as np
from autograd import jacobian
from scipy.integrate import quad

def line_integral(point1, point2):
    x1,y1,z1 = point1
    x2,y2,z2 = point2

    def F(X):
        x, y = X
        cong_factor = ((1/10*np.sin(x/100) + 1/100*np.sin(x/3) + 1/10*np.sin(x/10) + 1/10*np.sin(x/1000))*100 +
        (1/10*np.cos(y/100) + 1/100*np.cos(y/3) + 1/10*np.cos(y/10) + 1/10*np.cos(y/1000))*100)
        return cong_factor
    
    def r(t):        
        return np.array([(x2-x1)*t, (y2-y1)*t])
           
    def integrand(t):
        return F(r(t))

    I, e = quad(integrand, 0.0, 1.0)
    print(f'The integral is {I:1.4f}.')

line_integral((0,0,0),(1,1,1))
