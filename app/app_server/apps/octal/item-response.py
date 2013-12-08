import numpy as np
import scipy as sp

def sigmoid (theta=theta, a=a, b=b)
    bs = np.reshape(b, (len(b), 1))
    tmp = np.dot(a, theta)
    tmp = np.reshape(tmp,(len(tmp),1))
    return 1.0 / (1.0 + np.exp(bs - tmp))
    

theta_params = 2

numquestions = 10

theta_initial = np.zeros((theta_params))

theta = np.random.normal(loc=0, scale=1, size=theta_params)

a = np.random.normal(loc=1, scale=1, size=(numquestions,theta_params))

b = np.random.normal(loc=0, scale=1, size=(numquestions))

