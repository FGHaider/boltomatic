# This is a sample Python script.

# Press Skift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import math


class SafetyFactors:

    def __init__(self):

        self.verification_approach = 'analysis' # proto-type test, qualifcation or proto-flight test acceptance and proof
        self.sfy = 1.25
        self.sfu = 2.0
        self.sfgap = 1.2


class Fastener:

    def __init__(self):
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

        self.type = 'M' # or MJ

        # The following values apply for metric
        self.d2 = self.d * 0.64952 * self.p  # Pitch diameter
        self.d3 = self.d * 1.22687 * self.p  # Minor diameter
        if self.type == 'M':
            self.ds = 0.5*(self.d2 + self.d3)  # Diameter used for stress calculation M type thread
        elif self.type == 'MJ':
            self.ds = self.d3
        self.dsm = self.d3  # Diameter used for stiffness calculation
        self.duh = 0.5*(self.Dhead + self.Dh)  # Effective diameter of friction under head or nut
        if self.type == 'M':  # Stress area
            self.As = 0.25*math.pi*self.ds**2
        elif self.type == 'MJ':
            self.As = 0.25*math.pi*self.d3**2*(2-(self.d3/self.d2)**2)
        self.Asm = 0.25*math.pi*self.dsm**2 # stiffness area
        self.A0 = 0.25*math.pi*self.d0**2 # Smallest cross-section of fastener shank




def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
