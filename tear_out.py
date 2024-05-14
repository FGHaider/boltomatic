# Female thread

import numpy as np
import pandas as pd
import re


class Material:

    def __init__(self):
        self.sigma_y: float = 0
        self.sigma_u: float = 0
        self.alpha: float = 0
        self.youngs: float = 0


class Fastener:

    def __init__(self, size, pitch, material, tolerance, strength=None):
        """
        :param size: State size for example "M12"
        :param pitch: State pitch in mm
        :param material: Material name i.e. Stainless, Titanium etc.
        :param tolerance:
        :param strength: For example 8.8, if not stated defaults for material used
        """

        self.p: float = pitch  # Pitch of thread
        eth = MaleThread(size, pitch, tolerance)
        self.d, self.d1, self.d2, self.d3 = eth.fetch_geometry()
        # d:  Nominal fastener diameter Outside diameter of thread
        # d1: Pitch diameter
        # d2: Minor diameter
        # d3: Minor diameter of thread For the true thread, not the basic profile
        if tolerance is None:
            # The following values apply for metric
            self.d2 = self.d * 0.64952 * self.p  # Pitch diameter
            self.d3 = self.d * 1.22687 * self.p  # Minor diameter

        self.ultimate_str = None
        self.yield_str = None
        self.alpha = None

        self.material_name = material
        self.strength = strength
        self.set_material()
        ###########################################################################

        self.h: float = 0  # Height of the basic thread
        self.d0: float = 0  # Diameter at smallest cross‐section of fastener shank
        self.dsha: float = 0  # Shank diameter For necked‐down fasteners
        self.duh_brg: float = 0  # Outer diameter of bearing area   Either under head or under a nut
        self.Dh: float = 0  # Nominal diameter of hole in flange
        self.A0: float = 0  # Smallest cross‐section of fastener shank
        self.A3: float = 0  # Cross‐sectional area at minor diameter of fastener thread
        self.Lambda: float = 0  # Under‐head bearing angle Always 100º for countersunk aerospace standard fasteners(
        # right side of 851HFigure 5‐6)
        self.Sw: float = 0  # Size of wrenchAcross flats dimension of either ahead or a nut
        self.Dhead: float = 0  # Head diameter

        self.length: float = 0

        self.helix_angle: float = 0
        self.thread_grove_half_angle: float = 0
        self.under_head_bearing_angle: float = 0

        self.type = 'M'  # or MJ, MJ is a fatigue resistant thread used in aerospace
        self.dsm = self.d3  # Diameter used for stiffness calculation
        self.duh = 0.5 * (self.Dhead + self.Dh)  # Effective diameter of friction under head or nut

        if self.type == 'M':
            self.ds = 0.5 * (self.d2 + self.d3)  # Diameter used for stress calculation M type thread
            self.As = 0.25 * np.pi * self.ds ** 2
        elif self.type == 'MJ':
            self.ds = self.d3
            self.As = 0.25 * np.pi * self.d3 ** 2 * (2 - (self.d3 / self.d2) ** 2)

        self.Asm = 0.25 * np.pi * self.dsm ** 2  # stiffness area
        self.A0 = 0.25 * np.pi * self.d0 ** 2  # Smallest cross-section of fastener shank

    def set_material(self):

        data = pd.read_csv("./fastener_materials.csv", encoding='unicode_escape')
        matching = data.loc[data['Name'] == self.material_name]
        if matching.empty:
            raise Exception(f"The material '{self.material_name}' was not found in the database")
        self.ultimate_str = matching['Ultimate'].values
        self.yield_str = matching['Yield'].values
        self.alpha = matching['Alpha'].values

        if self.strength is not None:
            pattern = r'^\d{1,2}\.\d$'
            if re.match(pattern, self.strength):
                parts = self.strength.split('.')
                self.ultimate_str = int(parts[0]) * 1e2
                self.yield_str = int(parts[0]) * 1e2 * int(parts[-1]) / 10
            else:
                raise Exception("Strength definition incorrectly formatted, should be XX.X or X.X")


class MaleThread:
    def __init__(self, size, pitch, tolerance):

        data = pd.read_csv("./metric_external_thread.csv", encoding='unicode_escape')
        matching = data.loc[
            (data['Thread Designation'] == size + ' x ' + str(pitch)) & (data['Tolerance Class'] == tolerance)]

        if matching.empty:
            raise Exception("No matching thread size and tolerance was found in the dataset")

        self.d = [matching['d_min'].values, matching['d_max'].values]
        self.d2 = [matching['d2_min'].values, matching['d2_max'].values]
        self.d1 = matching['d1'].values
        self.d3 = matching['d3'].values

    def fetch_geometry(self, limit='min'):

        if limit == 'nominal':
            return np.mean(self.d), self.d1, np.mean(self.d2), self.d3
        elif limit == 'min':
            return np.min(self.d), self.d1, np.min(self.d2), self.d3
        elif limit == 'max':
            return np.max(self.d), self.d1, np.max(self.d2), self.d3
        else:
            raise Exception(f'{limit} is an unknown value type')


class FemaleThread:
    def __init__(self, size, pitch, tolerance='6H'):
        self.tolerance = tolerance

        data = pd.read_csv("./metric_internal_thread.csv", encoding='unicode_escape')
        matching = data.loc[
            (data['Thread Designation'] == size + ' x ' + str(pitch)) & (data['Tolerance Class'] == tolerance)]

        if matching.empty:
            raise Exception("No matching thread size and tolerance was found in the dataset")

        self.D = [matching['D_min'].values, matching['D_max'].values]
        self.D1 = [matching['D1_min'].values, matching['D1_max'].values]
        self.D2 = [matching['D2_min'].values, matching['D2_max'].values]

    def fetch_geometry(self, limit='min'):

        if limit == 'nominal':
            return np.mean(self.D), np.mean(self.D1), np.mean(self.D2)
        elif limit == 'min':
            return np.min(self.D), np.min(self.D1), np.min(self.D2)
        elif limit == 'max':
            return np.max(self.D), np.max(self.D1), np.max(self.D2)
        else:
            raise Exception(f'{limit} is an unknown value type')


class Thread:

    def __init__(self, size, pitch, tolerance_external, tolerance_internal='6H', nut=None):

        eth = MaleThread(size, pitch, tolerance_external)
        fth = FemaleThread(size, pitch, tolerance_internal)

        self.D, self.D1, self.D2 = fth.fetch_geometry()
        self.d, self.d1, self.d2, self.d3 = eth.fetch_geometry()

        self.sw = None
        self.tau_ult_n = 255
        self.tau_ult_b = 0.8 * 1200

        self.p = pitch
        self.phi = 30
        self.nut = nut
        self.Leng = 26
        self.Leng_eff = self.Leng - 2 * self.p

    def MOS(self, FA, sf, FVmax=None, force_ratio=1):

        Fcrit = min(self.Fult_th_n(), self.Fult_th_b())
        print(self.Fult_th_n())
        if FVmax is None:
            return Fcrit / (FA * sf) - 1
        else:
            return Fcrit / (FVmax + force_ratio * FA * sf) - 1

    def Fult_th_b(self):
        """
        Ultimate strength of the bolt threads
        """
        return self.tau_ult_b * self.Ath_b() * self.c1() * self.c2()

    def Fult_th_n(self):
        """
        Ultimate strength of the nut or hole threads
        """
        return self.tau_ult_n * self.Ath_n() * self.c1() * self.c2()

    def leng_req(self, Fth):
        """
         Thread length required for the bolt to fail before the hole/nut thread does
        """
        return Fth * self.p / (self.c1() * self.c2() * self.tau_ult_n * np.pi * self.d * (
                self.p / 2 + (self.d - self.d2) * np.tan(np.rad2deg(self.phi)))) + 0.8 * self.p

    def Rs(self):
        return self.tau_ult_n * self.Ath_n() / (self.tau_ult_b * self.Ath_b())

    def Ath_n(self):
        return np.pi * self.d * (self.Leng_eff / self.p) * (
                self.p / 2 + (self.d - self.D2) * np.tan(np.rad2deg(self.phi)))

    def Ath_b(self):
        return np.pi * self.D1 * (self.Leng_eff / self.p) * (
                self.p / 2 + (self.d2 - self.D1) * np.tan(np.rad2deg(self.phi)))

    def c1(self):
        if self.nut is not None:
            if 1.4 <= self.sw / self.D <= 1.9:
                return 3.8 * (self.sw / self.d) - (self.sw / self.d) ** 2 - 2.61
            else:
                raise f"The ratio sw/D is outside the required limits"

        else:
            return 1

    def c2(self):

        Rs = self.Rs()
        if 0.4 < Rs < 1:
            return 0.728 + 1.769 * Rs - 2.896 * Rs ** 2 + 1.296 * Rs ** 3
        elif Rs >= 1:
            return 0.897
        else:
            Rs = 0.4  # stated in latest handbook
            return 0.728 + 1.769 * Rs - 2.896 * Rs ** 2 + 1.296 * Rs ** 3



def shear_out(a, t, tau_ult, sf_ult, FQ):
    return (2 * tau_ult * a * t) / (FQ * sf_ult) - 1


if __name__ == '__main__':
    th = Thread('M12', 1.75, '6g')
    print(th.Fult_th_n())
    #print(th.Fult_th_b())
    print(th.MOS(FA=20e3, sf=1.5, FVmax=55e3))
    print(shear_out(18, 3, 255, 1.61, 15000))
