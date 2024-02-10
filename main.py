# This is a sample Python script.

# Press Skift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import math
import numpy as np


def coefficient_of_utilisation(pretension_stress=None, yield_stress=None):
    """
    Calculates utilisation according to eq. 6.2.1 and implements design reference values
    :param pretension_stress:
    :param yield_stress:
    :return:
    """
    if pretension_stress is None or yield_stress is None:
        utilisation = 0.65
    else:
        utilisation = pretension_stress / yield_stress
        if utilisation > 0.8 or utilisation < 0.5:
            print("A coefficient of utilisation of 0.5 to 0.8 is typical, the utilisation is outside this range")
    return utilisation


def nominal_preload(utilisation, yield_stress, stress_area):
    """
    Implements equation 6.2.2.
    :param utilisation:
    :param yield_stress:
    :param stress_area:
    :return:
    """
    return utilisation * yield_stress * stress_area


class SafetyFactors:

    def __init__(self):
        self.verification_approach = 'analysis'  # proto-type test, qualifcation or proto-flight test acceptance and proof
        self.sfy = 1.25
        self.sfu = 2.0
        self.sfgap = 1.2


class Joint:

    def __init__(self):
        self.head_friction: float = 0
        self.head_friction_min: float = 0
        self.head_friction_max: float = 0

        self.thread_friction: float = 0
        self.thread_friction_min: float = 0
        self.thread_friction_max: float = 0


class Material:

    def __init__(self):
        self.sigma_y: float = 0
        self.sigma_u: float = 0
        self.alpha: float = 0
        self.youngs: float = 0


class Fastener(Material):

    def __init__(self):
        super().__init__()
        self.p: float = 0  # Pitch of thread
        self.h: float = 0  # Height of the basic thread
        self.d: float = 0  # Nominal fastener diameter Outside diameter of thread
        self.d0: float = 0  # Diameter at smallest cross‐section of fastener shank
        self.d3: float = 0  # Minor diameter of thread For the true thread, not the basic profile
        self.dsha: float = 0  # Shank diameter For necked‐down fasteners
        self.duh_brg: float = 0  # Outer diameter of bearing area   Either undea head or under anut
        self.Dh: float = 0  # Nominal diameter of hole in flange
        self.A0: float = 0  # Smallest cross‐section of fastener shank
        self.A3: float = 0  # Cross‐sectional area at minor diameter offastener thread
        self.Lambda: float = 0  # Under‐head bearing angle Always 100º for countersunk aerospace standard fasteners(right side of 851HFigure 5‐6)
        self.Sw: float = 0  # Size of wrenchAcross flats dimension of either ahead or a nut
        self.Dhead: float = 0  # Head diameter

        self.length: float = 0

        self.type = 'M'  # or MJ

        # The following values apply for metric
        self.d2 = self.d * 0.64952 * self.p  # Pitch diameter
        self.d3 = self.d * 1.22687 * self.p  # Minor diameter
        if self.type == 'M':
            self.ds = 0.5 * (self.d2 + self.d3)  # Diameter used for stress calculation M type thread
        elif self.type == 'MJ':
            self.ds = self.d3
        self.dsm = self.d3  # Diameter used for stiffness calculation
        self.duh = 0.5 * (self.Dhead + self.Dh)  # Effective diameter of friction under head or nut
        if self.type == 'M':  # Stress area
            self.As = 0.25 * math.pi * self.ds ** 2
        elif self.type == 'MJ':
            self.As = 0.25 * math.pi * self.d3 ** 2 * (2 - (self.d3 / self.d2) ** 2)
        self.Asm = 0.25 * math.pi * self.dsm ** 2  # stiffness area
        self.A0 = 0.25 * math.pi * self.d0 ** 2  # Smallest cross-section of fastener shank

        self.helix_angle: float = 0
        self.thread_grove_half_angle: float = 0
        self.under_head_bearing_angle: float = 0


def wedge_model(preload, joint, fastener: Fastener, prevailing_torque=0):
    """
    Implements the wedge model described in chapter 6.3.1
    :param prevailing_torque: self-locking torque of a locking device
    :param fastener:
    :param preload:
    :param thread_friction:
    :param head_friction, coefficient of friction between the nut (or fastener head) and the adjacent clamped part
    :return:
    """

    rho = math.atan(joint.thread_friction / math.cos(fastener.thread_grove_half_angle))  # eq. 6.3.2
    slip_wedge_force = preload * math.tan(fastener.helix_angle + rho)  # 6.3.1
    torque_thread_interface = preload * math.tan(fastener.helix_angle + rho) * fastener.d2 / 2  # 6.3.3
    torque_under_head = preload * (joint.head_friction * fastener.duh) / 2 * 1 / (
        math.sin(fastener.under_head_bearing_angle / 2))  # 6.3.4
    # installation_torque = torque_thread_interface + torque_under_head + prevailing_torque # To achieve the given preload 6.3.5

    p = math.tan(fastener.helix_angle) * math.pi * fastener.duh  # 6.3.9  # Possibly move to fastener definition
    torque_absorbed_stretching = preload * p / (2 * math.pi)
    torque_absorbed_thread_friction = preload * fastener.d2 * joint.thread_friction / (
                2 * math.cos(fastener.thread_grove_half_angle / 2))
    torque_absorbed_head_friction = preload * (joint.head_friction * fastener.duh) / (
                2 * math.sin(fastener.under_head_bearing_angle / 2))
    # 6.3.10
    installation_torque = torque_absorbed_stretching + torque_absorbed_head_friction + torque_absorbed_thread_friction + prevailing_torque

    return installation_torque


# Determination of design torque level
"""
Excessive fastener torque can lead to tensile failure of the fastener. On the other hand, insufficient torque
can lead to inadequate compression of the clamped parts, leading to failure by gapping or to slipping
(when slipping is not allowed).
The specified torque range is normally found by an iterative design process whereby the margins of safety
are calculated for each relevant failure mode.
The maximum and minimum applied torques, Mapp,max and Mapp,min, should first be calculated taking into
account the torque measurement accuracy. The most common way to specify these torque levels is toECSS‐E‐HB‐32‐23A
16 April 2010
50
calculate them relative to a nominal applied torque, Mnom. Appendix A recommends starting values of
nominal torque, Mapp,nom, for some of the most commonly used fasteners.
Two methods are presented below for calculating the preload range based on the torque range:
a. Experimental Coefficient Method, and
b. Typical Coefficient Method.
The Experimental Coefficient Method should be applied whenever the preload in the joint is critical (e.g.
for friction grip joints) since it considers independently the uncertainties of the fastener friction
coefficients and torque wrench accuracy.
The Typical Coefficient Method is mostly used in cases where control of the preload is non‐critical. This
occurs most often for bearing joints or low‐duty joints.
"""

def mos_tightening(fastener, joint, FVmax, Ftemp_pos, Mapp_max):
    # Chapter 6.5

    Muh_min = fastener.duh/2 * (FVmax - Ftemp_pos)*joint.head_friction_min
    Wp = math.pi*fastener.d0**3/16
    Wp_reduced = math.pi*fastener.d0**3/12 # see eq.6.5.5 unclear where it is applicable

    shear_max = (Mapp_max - Muh_min)/Wp
    sigma_max_axial_stress_preload = (FVmax + Ftemp_pos)/fastener.A0

    sigma_vm = math.sqrt(sigma_max_axial_stress_preload**2 + 3*shear_max**2)
    mosy = fastener.sigma_yield/sigma_vm - 1
    mosu = fastener.sigma_ultimate / sigma_vm - 1

    return mosy, mosu


def embedding(fz, disp_b, disp_c, preload=None):
    if preload is None:
        Fz = fz / (disp_b + disp_c)
    else:  # Uncritical cases assumption see eq. 6.4.3
        Fz = 0.05*preload

    return Fz


def multipart_thermal_preload(fastener, lengths: np.array, thermals: np.array, temp_diff, load_factor, length_joint):
    # Chapter 6.3.5.2, does not take temperature dependent youngs into consideration
    preload_thermal = (np.sum(thermals*lengths)-fastener.alpha*fastener.length)/length_joint * \
                      temp_diff*fastener.youngs*fastener.Asm*(1-load_factor)

    return preload_thermal


def experimental_coefficient_partial(fastener, thread_friction, head_friction):
    compression_cone_half_angle = 0
    return (fastener.d2 / 2 * (math.tan(compression_cone_half_angle) +
                               thread_friction / (math.cos(fastener.thread_grove_half_angle / 2))) +
            1 / 2 * fastener.duh * head_friction)


def experimental_coefficient_method(omega, Mnom, thermal_fastener_load_positive, thermal_fastener_load_negative,
                                    fastener, joint, Fz, MPmin, MPmax):
    """
    Chapter 6.3.2.2
    This method takes into account all sources of preload uncertainty, namely the prevailing torque, preload
    loss due to embedding, thermo‐elastic effects, and the torque wrench accuracy.
    :param Mnom: nominal applied torque determined by iterative process
    :param omega: torque wrench accuracy +-5 to +-15 % typical
    :return:
    """

    Mapp_max = (1 + omega) * Mnom  # 6.3.12
    Mapp_min = (1 - omega) * Mnom  # 6.3.13

    # eq. 6.3.14 and 6.3.15
    preload_max = (Mapp_max - MPmin) / \
                  experimental_coefficient_partial(fastener, joint.thread_friction_min, joint.head_friction_min) \
                  + thermal_fastener_load_positive
    preload_min = (Mapp_min - MPmax) / \
                  experimental_coefficient_partial(fastener, joint.thread_friction_max, joint.head_friction_max) \
                  + thermal_fastener_load_negative - Fz

    return preload_max, preload_min


def typical_coefficient_method(omega, Mnom, thermal_fastener_load_positive, thermal_fastener_load_negative,
                                    fastener, joint, Fz, MPmax, uncertainty_factor):

    Mapp_max = (1 + omega) * Mnom  # 6.3.12
    Mapp_min = (1 - omega) * Mnom  # 6.3.13

    # eq. 6.3.16 and 6.3.17
    preload_max = ((1+uncertainty_factor)*Mapp_max) / \
                  experimental_coefficient_partial(fastener, joint.thread_friction, joint.head_friction) \
                  + thermal_fastener_load_positive
    preload_min = (1-uncertainty_factor)*(Mapp_min - MPmax) / \
                  experimental_coefficient_partial(fastener, joint.thread_friction, joint.head_friction) \
                  + thermal_fastener_load_negative - Fz

    return preload_max, preload_min


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
