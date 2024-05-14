
import numpy as np

# Ultimate and yield design loads follow below
def Pu(FF, FSu, PL):
    """
    :param FF: Fitting factor
    :param FSu: Safety factor
    :param PL: Limit load
    :return:
    """
    return FF*FSu*PL


def Py(FF, FSy, PL):
    return FF*FSy*PL


def MS(Papo, FF, FS, PL):
    return Papo/(FF*FS*PL) - 1


def Ppmax(Ppimax, Pdeltatmax):
    return Ppimax + Pdeltatmax

def Ppmin(Ppimin, Ppr, Ppc, Pdeltatmin):
    Ppimin - Ppr - Ppc - Pdeltatmin

def Ppimax(cmax, Gamma, Ppinom):
    return cmax*(1+Gamma)*Ppinom

def Ppimin(cmin, Gamma, Ppinom):
    return cmin*(1+Gamma)*Ppinom

def Ppimin_sep_non_critical(cmin, Gamma, nf, Ppinom):
    return cmin*(1-Gamma/np.sqrt(nf))*Ppinom