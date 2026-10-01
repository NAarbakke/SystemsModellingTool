"""
You give it:
    - Air conditions in and out  (from your cycle code)
    - Coolant conditions in      (from your reactor model)
    - A few design choices       (wall material, wall thickness, etc.)

It gives you:
    - Required heat transfer area  [m^2]
    - Coolant outlet temperature   [K]
    - Overall heat transfer coefficient U  [W/(m^2 K)]
    - Pressure drop estimates
    - Temperature profiles along the exchanger

HOW IT WORKS (the short version)
---------------------------------
1. Energy balance:  Q = mdot_air * cp_air * (T_air_out - T_air_in)
   This tells you how much heat you need.  No unknowns here.

2. Same Q must come from the coolant:
   Q = mdot_coolant * cp_coolant * (T_coolant_in - T_coolant_out)
   So you can solve for T_coolant_out directly.  Still no unknowns.

3. Now you know all four temperatures.  The driving force for heat
   transfer is the temperature difference between hot and cold streams,
   which varies along the exchanger.  The log-mean temperature
   difference (LMTD) captures this as a single effective average.

4. The overall heat transfer coefficient U captures how easily heat
   crosses from coolant to air:
       1/U  =  1/h_coolant  +  t_wall/k_wall  +  1/h_air
   Each term is a thermal resistance (like electrical resistors in series).

5. Finally:  A = Q / (U * LMTD)
   That's your required heat transfer area.

NO ITERATION NEEDED because you already know the cold-side outlet
(it's your required turbine entry temperature) and the energy balance
gives you the hot-side outlet directly.

The code also chops the exchanger into segments to capture how fluid
properties change with temperature.  This is just a refinement - the
basic logic above still applies, just segment by segment.
"""

import numpy as np
from dataclasses import dataclass
from properties.materials.hx_walls.possible_materials import WALLS
from subsystems.propulsion.coolants.possible_coolants import FLUIDS
from subsystems.propulsion.motors.components.base_component import Component
from subsystems.propulsion.motors.helpers.flow_state import FlowState
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.components.heat_exchangers.heat_exchanger_specs import HeatExchangerSpecs


def compute_h(fluid_props, mdot, n_channels, D_h):
    """Compute convective heat transfer coefficient from flow conditions.

    Parameters
    ----------
    fluid_props : dict   Output from one of the property functions above
    mdot        : float  Mass flow rate [kg/s]
    n_channels  : int    Number of parallel channels
    D_h         : float  Hydraulic diameter of one channel [m]

    Returns
    -------
    h   : float  Heat transfer coefficient [W/(m^2 K)]
    u   : float  Flow velocity [m/s]
    Re  : float  Reynolds number
    dP_per_m : float  Pressure drop per metre of channel [Pa/m]
    """
    rho = fluid_props["rho"]
    mu  = fluid_props["mu"]
    k   = fluid_props["k"]
    Pr  = fluid_props["Pr"]
    #cp  = fluid_props["cp"]

    # Flow area and velocity
    A_channel = np.pi * D_h**2 / 4    # approximate for any shape
    A_total   = n_channels * A_channel
    u         = mdot / (rho * A_total)

    # Reynolds number
    Re = rho * u * D_h / mu

    # Nusselt number (pick correlation based on Prandtl number)
    if Pr < 0.1:
        # LIQUID METAL:  Lyon-Martinelli
        Pe = Re * Pr
        Nu = 7.0 + 0.025 * Pe**0.8
    elif Re < 2300:
        # LAMINAR
        Nu = 4.36
    else:
        # TURBULENT (gases, molten salts):  Gnielinski
        f  = (0.790 * np.log(max(Re, 3000)) - 1.64)**(-2)
        Nu = (f / 8) * (Re - 1000) * Pr / (1 + 12.7 * np.sqrt(f / 8) * (Pr**(2/3) - 1))
        Nu = max(Nu, 4.36)

    # h from Nusselt number:  Nu = h * D_h / k  =>  h = Nu * k / D_h
    h = Nu * k / D_h

    # Pressure drop per metre (Darcy-Weisbach)
    if Re < 2300:
        f = 64 / max(Re, 1)
    else:
        f = (0.790 * np.log(max(Re, 3000)) - 1.64)**(-2)
    dP_per_m = f / D_h * 0.5 * rho * u**2

    return h, u, Re, dP_per_m



@dataclass
class HXResult:
    """Everything the sizing calculation produces."""
    Q: float              # Heat duty [W]
    A: float              # Required heat transfer area [m^2]
    U_avg: float          # Average overall HTC [W/(m^2 K)]
    LMTD: float           # Log-mean temperature difference [K]
    T_hot_out: float      # Coolant outlet temperature [K]
    effectiveness: float  # Q / Q_max
    dP_cold: float        # Cold-side pressure drop [Pa]
    dP_hot: float         # Hot-side pressure drop [Pa]

    # Temperature profiles (for plotting)
    x: np.ndarray                  # position along HX [0 to 1]
    T_cold: np.ndarray             # cold-side temperature [K]
    T_hot: np.ndarray              # hot-side temperature [K]
    U_local: np.ndarray            # local U [W/(m^2 K)]

    def summary(self):
        print("=" * 55)
        print("  HEAT EXCHANGER SIZING RESULTS")
        print("=" * 55)
        print(f"  Heat duty          : {self.Q / 1e6:.3f} MW")
        print(f"  Required area      : {self.A:.1f} m^2")
        print(f"  Average U          : {self.U_avg:.1f} W/(m^2 K)")
        print(f"  LMTD               : {self.LMTD:.1f} K")
        print(f"  Effectiveness      : {self.effectiveness:.4f}")
        print(f"  Coolant outlet     : {self.T_hot_out:.1f} K")
        print(f"  Air-side dP        : {self.dP_cold / 1e3:.1f} kPa "
              f"({self.dP_cold / (self.dP_cold + 1) * 100:.1f}%)")
        print(f"  Coolant-side dP    : {self.dP_hot / 1e3:.1f} kPa")
        print("=" * 55)


class HeatExchanger:
    """Generic counterflow heat exchanger sizing.

    Parameters
    ----------
    # --- From your cycle code ---
    cold_fluid   : str     "air", "helium", etc.
    T_cold_in    : float   Compressor outlet temperature [K]
    T_cold_out   : float   Required turbine entry temperature [K]
    P_cold       : float   Compressor outlet pressure [Pa]
    mdot_cold    : float   Air mass flow rate [kg/s]

    # --- From your reactor model ---
    hot_fluid    : str     "sodium", "nak", "flinak", etc.
    T_hot_in     : float   Coolant temperature leaving reactor [K]
    P_hot        : float   Coolant pressure [Pa]
    mdot_hot     : float   Coolant mass flow rate [kg/s]

    # --- Design choices (all have defaults) ---
    wall_material   : str    Wall material name (default "inconel_617")
    t_wall          : float  Wall thickness [m]  (default 1 mm)
    n_channels_cold : int    Number of cold-side channels (for computing h)
    n_channels_hot  : int    Number of hot-side channels (for computing h)
    D_h_cold        : float  Cold-side hydraulic diameter [m]
    D_h_hot         : float  Hot-side hydraulic diameter [m]
    n_segments      : int    Number of segments for discretisation
    """

    def __init__(self,
        # Cold side (air)
        cold_fluid: str,
        T_cold_in: float,
        T_cold_out: float,
        P_cold: float,
        mdot_cold: float,

        # Hot side (coolant)
        hot_fluid: str,
        T_hot_in: float,
        P_hot: float,
        mdot_hot: float,

        # Design parameters
        wall_material: str = "inconel_617",
        t_wall: float = 1.0e-3,

        # Channel geometry for computing h
        n_channels_cold: int = 50000,
        n_channels_hot:  int = 50000,
        D_h_cold: float = 2.0e-3,
        D_h_hot:  float = 2.0e-3,

        # Solver
        n_segments: int = 50):

        self.cold_fluid = cold_fluid
        self.T_cold_in  = T_cold_in
        self.T_cold_out = T_cold_out
        self.P_cold     = P_cold
        self.mdot_cold  = mdot_cold

        self.hot_fluid = hot_fluid
        self.T_hot_in  = T_hot_in
        self.P_hot     = P_hot
        self.mdot_hot  = mdot_hot

        self.wall_material = wall_material
        self.t_wall = t_wall
        self.n_channels_cold = n_channels_cold
        self.n_channels_hot  = n_channels_hot
        self.D_h_cold = D_h_cold
        self.D_h_hot  = D_h_hot
        self.N = n_segments

        # Look up property functions
        self.cold_props_fn = FLUIDS[cold_fluid]
        self.hot_props_fn  = FLUIDS[hot_fluid]
        self.wall_k_fn     = WALLS[wall_material]["k"]
        self.wall_rho      = WALLS[wall_material]["rho"]

    def solve(self) -> HXResult:
        """Size the heat exchanger.  Returns an HXResult."""

        N = self.N

        # ==============================================================
        # STEP 1:  Energy balance  (no unknowns)
        # ==============================================================
        # Average cold-side cp (property varies with T, so use midpoint)
        T_c_avg = 0.5 * (self.T_cold_in + self.T_cold_out)
        cp_cold = self.cold_props_fn(T_c_avg, self.P_cold)["cp"]

        Q = self.mdot_cold * cp_cold * (self.T_cold_out - self.T_cold_in)

        # ==============================================================
        # STEP 2:  Hot-side outlet from energy balance
        # ==============================================================
        # First estimate using cp at hot inlet
        cp_hot_est = self.hot_props_fn(self.T_hot_in, self.P_hot)["cp"]
        T_hot_out = self.T_hot_in - Q / (self.mdot_hot * cp_hot_est)

        # Refine with cp at average hot temperature
        T_h_avg = 0.5 * (self.T_hot_in + T_hot_out)
        cp_hot = self.hot_props_fn(T_h_avg, self.P_hot)["cp"]
        T_hot_out = self.T_hot_in - Q / (self.mdot_hot * cp_hot)

        # ==============================================================
        # STEP 3:  March along the exchanger, segment by segment
        # ==============================================================
        # Counterflow:  cold goes left-to-right, hot goes right-to-left.
        #
        #   position:     0 -----> 1
        #   cold:    T_cold_in  -->  T_cold_out
        #   hot:     T_hot_out  <--  T_hot_in
        #
        # So at position 0:  cold is coldest, hot is at its outlet (coolest)
        # At position 1:     cold is hottest, hot is at its inlet (hottest)

        T_c = np.linspace(self.T_cold_in, self.T_cold_out, N + 1)
        T_h = np.linspace(T_hot_out, self.T_hot_in, N + 1)

        U_arr  = np.zeros(N)      # local overall HTC for each segment
        dA_arr = np.zeros(N)      # area needed for each segment
        dP_c_arr = np.zeros(N)    # pressure drop per segment (cold)
        dP_h_arr = np.zeros(N)    # pressure drop per segment (hot)

        dQ = Q / N   # heat transferred per segment (uniform by energy balance)

        for i in range(N):
            # Midpoint temperatures for this segment
            T_c_mid = 0.5 * (T_c[i] + T_c[i + 1])
            T_h_mid = 0.5 * (T_h[i] + T_h[i + 1])

            # --- Fluid properties at local temperature ---
            props_c = self.cold_props_fn(T_c_mid, self.P_cold)
            props_h = self.hot_props_fn(T_h_mid, self.P_hot)

            # --- Wall conductivity at average wall temperature ---
            T_wall = 0.5 * (T_c_mid + T_h_mid)
            k_wall = self.wall_k_fn(T_wall)

            # --- Heat transfer coefficients ---
            h_c, _, _, dP_c_per_m = compute_h(
                props_c, self.mdot_cold,
                self.n_channels_cold, self.D_h_cold)

            h_h, _, _, dP_h_per_m = compute_h(
                props_h, self.mdot_hot,
                self.n_channels_hot, self.D_h_hot)

            # --- Overall U for this segment ---
            # Three resistances in series:
            #   1/h_cold  +  t_wall/k_wall  +  1/h_hot
            U_local = 1.0 / (1.0 / h_c + self.t_wall / k_wall + 1.0 / h_h)

            # --- Local temperature difference ---
            dT = T_h_mid - T_c_mid
            dT = max(dT, 1.0)     # safety clamp

            # --- Required area for this segment ---
            #     dQ = U * dA * dT   =>   dA = dQ / (U * dT)
            dA_arr[i] = dQ / (U_local * dT)
            U_arr[i]  = U_local

            # --- Pressure drop contribution ---
            dP_c_arr[i] = dP_c_per_m   # per metre; we'll multiply by length later
            dP_h_arr[i] = dP_h_per_m

            # --- Update temperatures using local cp ---
            T_c[i + 1] = T_c[i] + dQ / (self.mdot_cold * props_c["cp"])
            T_h[i + 1] = T_h[i] + dQ / (self.mdot_hot * props_h["cp"])

        # ==============================================================
        # STEP 4:  Totals
        # ==============================================================
        A_total = np.sum(dA_arr)
        U_avg   = Q / (A_total * self._compute_LMTD(T_c, T_h)) if A_total > 0 else 0

        LMTD = self._compute_LMTD(T_c, T_h)

        # Effectiveness
        C_cold = self.mdot_cold * cp_cold
        C_hot  = self.mdot_hot * cp_hot
        C_min  = min(C_cold, C_hot)
        Q_max  = C_min * (self.T_hot_in - self.T_cold_in)
        effectiveness = Q / Q_max if Q_max > 0 else 0

        # Pressure drops (need length estimate)
        # Rough length:  A_total = perimeter * L * n_channels
        #   perimeter ~ pi * D_h,  so  L ~ A / (n_channels * pi * D_h)
        L_est = A_total / (self.n_channels_cold * np.pi * self.D_h_cold)
        dP_cold = np.mean(dP_c_arr) * L_est
        dP_hot  = np.mean(dP_h_arr) * L_est

        return HXResult(
            Q=Q, A=A_total,
            U_avg=U_avg,
            LMTD=LMTD,
            T_hot_out=T_h[0],
            effectiveness=effectiveness,
            dP_cold=dP_cold,
            dP_hot=dP_hot,
            x=np.linspace(0, 1, N + 1),
            T_cold=T_c,
            T_hot=T_h,
            U_local=U_arr)

    def _compute_LMTD(self, T_c, T_h):
        """Log-mean temperature difference for counterflow."""
        # At position 0 (cold inlet):   dT = T_hot_out - T_cold_in
        # At position N (cold outlet):  dT = T_hot_in  - T_cold_out
        dT1 = T_h[0]  - T_c[0]     # hot outlet end
        dT2 = T_h[-1] - T_c[-1]    # hot inlet end

        dT1 = max(dT1, 0.1)
        dT2 = max(dT2, 0.1)

        if abs(dT1 - dT2) < 0.01:
            return dT1    # they're equal, LMTD = either one

        return (dT1 - dT2) / np.log(dT1 / dT2)


# ====================================================================
#  COMPONENT WRAPPER  (integrates HeatExchanger into the engine chain)
# ====================================================================

class HeatExchangerComponent(Component):
    """Wraps HeatExchanger as a Component so it slots into the engine like a Combustor.

    Cold side (air) comes from the incoming FlowState (compressor exit).
    Hot side (reactor coolant) parameters are fixed at construction.

    process(flow) -> FlowState with:
        Tt  = T_cold_out   (target turbine entry temperature)
        Pt  = flow.Pt - dP_cold   (pressure drop from HX physics)
        m_dot unchanged   (no fuel addition in nuclear cycle)
    """

    def __init__(self, specs: HeatExchangerSpecs, gas_model: GasModel = None, name: str = "heat_exchanger"):
        super().__init__(gas_model, name)

        self.T_cold_out = specs.T_cold_out

        # Hot-side params (fixed at construction)
        self.hot_fluid = specs.hot_fluid
        self.T_hot_in = specs.T_hot_in
        self.P_hot = specs.P_hot
        self.mdot_hot = specs.mdot_hot

        # Design params
        self.wall_material = specs.wall_material
        self.t_wall = specs.t_wall
        self.n_channels_cold = specs.n_channels_cold
        self.n_channels_hot = specs.n_channels_hot
        self.D_h_cold = specs.D_h_cold
        self.D_h_hot = specs.D_h_hot
        self.n_segments = specs.n_segments

        self.last_hx_result: HXResult | None = None

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow

        hx = HeatExchanger(
            cold_fluid="air",
            T_cold_in=flow.Tt,
            T_cold_out=self.T_cold_out,
            P_cold=flow.Pt,
            mdot_cold=flow.m_dot,

            hot_fluid=self.hot_fluid,
            T_hot_in=self.T_hot_in,
            P_hot=self.P_hot,
            mdot_hot=self.mdot_hot,

            wall_material=self.wall_material,
            t_wall=self.t_wall,
            n_channels_cold=self.n_channels_cold,
            n_channels_hot=self.n_channels_hot,
            D_h_cold=self.D_h_cold,
            D_h_hot=self.D_h_hot,
            n_segments=self.n_segments)

        result = hx.solve()
        self.last_hx_result = result

        Pt_out = flow.Pt - result.dP_cold

        out = FlowState(
            Tt=self.T_cold_out,
            Pt=Pt_out,
            m_dot=flow.m_dot)

        self.last_exit = out
        return out
