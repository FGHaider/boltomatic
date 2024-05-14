"""
Implements the three different methods presented on https://engineeringlibrary.org/reference/bolted-joint-design-analysis-sandia
"""

import numpy as np

def shigley_frustrum():

    E = 1
    db = 1
    dh = 1
    l= 1
    alpha = 1
    ki = np.pi*E*db*np.tan(alpha)/(np.log(((2*l*np.tan(alpha) + dh - db)*(dh + db)) /
                                          ((2*l*np.tan(alpha) + dh + db)*(dh - db))))

def cylindrical_stress_field_method():
    # Also called Q Factor
    dc = 1
    d = 1 # bolt diameter
    Ai = 1
    Ei = 1
    Li = 1
    db = 1
    qi = 1
    q = 1
    dh = 1 # bolt head diameter
    Dj = 1
    l = 1

    Q = dc/d
    ki = Ai*Ei/Li
    Ai = np.pi/4*db**2*(Q**2-qi**2)
    Ii = np.pi/64*((Q*db)**4 - (qi*db)**4)
    kbendingi = Ei*Ii/Li
    kbending = np.pi*db**4/64*np.sum(Ei*(Q**4-qi**4)/Li)

    if dh >= Dj:
        A = np.pi/4*((Q*db)**2-(q*db)**2)
        Q = Dj/d  # when dh >= Dj

    elif dh < Dj <= 3*dh:
        A = np.pi/4*(dh**2-(q*db)**2) + np.pi/8*(Dj/dh - 1)*(dh*l/5+l**2/100)
        Q = 1/d*np.sqrt(dh**2 + (Dj/dh - 1)*(dh*l/10+l**2/200))

    elif Dj > 3*dh and l <= 8*dh:
        A = np.pi/4*((dh+l/10)**2-(q*db)**2)
        Q = 1/db*(dh + l/10)