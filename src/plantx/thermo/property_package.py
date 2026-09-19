"""Property Package Abstraction & Ideal Gas Engine for Stage 13."""

import hashlib
import json
from typing import Dict, Any, Optional
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.thermo.schemas import (
    ThermodynamicInput,
    ThermodynamicState,
    PropertyPackageType,
    PhaseState,
    CompositionBasis,
)
from src.plantx.thermo.errors import ThermoValidationError


class PropertyPackage:
    """Base abstract property package."""

    @staticmethod
    def evaluate_state(inp: ThermodynamicInput) -> ThermodynamicState:
        raise NotImplementedError()


class IdealGasPackage(PropertyPackage):
    """Analytical Ideal Gas Law Property Package P * V = n * R * T."""

    R_UNIVERSAL = 8.314462618  # J/(mol*K)

    @staticmethod
    def evaluate_state(inp: ThermodynamicInput) -> ThermodynamicState:
        if inp.temperature <= 0:
            raise ThermoValidationError(f"Invalid temperature {inp.temperature} K. Temperature must be strictly > 0 K.")
        if inp.pressure < 0:
            raise ThermoValidationError(f"Invalid pressure {inp.pressure} Pa. Pressure must be >= 0.")

        mw = 28.97  # Default molecular weight for dry air in g/mol if composition unspecified
        if inp.composition and inp.composition_basis != CompositionBasis.UNKNOWN:
            # Simple weighted molecular weight if components provided
            comp_mw_map = {"Methane": 16.04, "Ethane": 30.07, "Propane": 44.10, "N2": 28.01, "O2": 31.99}
            tot_w = sum(inp.composition.values())
            if abs(tot_w - 1.0) > 0.05:
                raise ThermoValidationError(f"Composition sum {tot_w} deviates from 1.0 without explicit basis.")
            calc_mw = sum(frac * comp_mw_map.get(comp, 28.97) for comp, frac in inp.composition.items())
            if calc_mw > 0:
                mw = calc_mw

        r_specific = (IdealGasPackage.R_UNIVERSAL / (mw / 1000.0))  # J/(kg*K)

        # Density: rho = P / (R_sp * T)
        density = inp.pressure / (r_specific * inp.temperature)
        spec_vol = 1.0 / density if density > 0 else None

        # Sensible enthalpy for constant Cp = 1005 J/(kg*K)
        cp = 1005.0
        cv = cp - r_specific
        enthalpy = cp * inp.temperature
        internal_energy = cv * inp.temperature

        prov = Provenance(
            provenance_id=f"prov-thermo-{int(inp.temperature)}-{int(inp.pressure)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="IdealGasPackage.evaluate_state",
            timestamp="2026-09-17T15:35:00Z",
            transformation_applied="Stage 13 Ideal Gas Analytical Property Evaluation",
        )

        res_data = json.dumps({"T": inp.temperature, "P": inp.pressure, "rho": density}, sort_keys=True)
        res_hash = hashlib.sha256(res_data.encode("utf-8")).hexdigest()

        return ThermodynamicState(
            state_id=f"state-{int(inp.temperature)}-{int(inp.pressure)}",
            temperature=inp.temperature,
            pressure=inp.pressure,
            composition=inp.composition,
            composition_basis=inp.composition_basis,
            phase=PhaseState.VAPOR if inp.phase_hint == PhaseState.UNKNOWN else inp.phase_hint,
            density=density,
            specific_volume=spec_vol,
            enthalpy=enthalpy,
            internal_energy=internal_energy,
            entropy=None,
            heat_capacity_cp=cp,
            heat_capacity_cv=cv,
            viscosity=None,  # Explicitly UNAVAILABLE per dataset limits
            thermal_conductivity=None,
            compressibility_factor=1.0,
            property_package=PropertyPackageType.IDEAL_GAS,
            calculation_method="ANALYTICAL_IDEAL_GAS",
            truth_state=TruthState.INFERRED,
            applicability="VALIDATED_IDEAL_GAS_DOMAIN",
            provenance=prov,
            result_hash=res_hash,
        )
