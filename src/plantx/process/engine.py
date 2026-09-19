"""Representative crude unit refinery process graph generator & FOUL-X asset dataset mapper."""

from typing import Dict, Any, Tuple
from pathlib import Path
import hashlib

from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.process.schemas import (
    PlantModel,
    ProcessUnit,
    EquipmentModel,
    HeatExchangerModel,
    ProcessStream,
    ProcessConnection,
    MeasurementBinding,
    EquipmentType,
    StreamPhase,
    ConnectionType,
    EntityResolutionState,
)
from src.plantx.process.graph import GraphEngine, PlantGraph


class ProcessModelEngine:
    """Builds representative crude distillation unit (CDU) computational plant model."""

    @staticmethod
    def create_representative_cdu_model(
        plant_id: str = "CDU-PLANT-01",
        eval_timestamp: float = 1000.0,
        baseline_max_time: float = 63999.0,
        data_path: Path = Path("data/raw/heat_exchanger_fouling_dataset.csv"),
    ) -> Tuple[PlantModel, PlantGraph]:
        # Source immutability check
        h_before = hashlib.sha256(data_path.read_bytes()).hexdigest()

        if eval_timestamp > baseline_max_time:
            from src.plantx.process.errors import TemporalProcessGraphViolation
            raise TemporalProcessGraphViolation(f"Timestamp {eval_timestamp} exceeds baseline max time {baseline_max_time}")

        prov = Provenance(
            provenance_id=f"prov-cdu-{int(eval_timestamp)}",
            provenance_type=ProvenanceType.REPRESENTATIVE_TEMPLATE,
            source_reference="Representative CDU Process Topology",
            timestamp="2026-09-17T15:10:00Z",
            transformation_applied="Stage 11 Process Model Construction",
        )

        model = PlantModel(
            plant_id=plant_id,
            name="Representative Crude Distillation Plant",
            description="Representative process topology — synthetic / illustrative.",
            provenance=prov,
            truth_state=TruthState.REPRESENTATIVE,
        )

        # 1. Process Unit
        unit_cdu = ProcessUnit(
            unit_id="CDU-100",
            name="Crude Distillation Unit 100",
            unit_type="DISTILLATION_UNIT",
            provenance=prov,
            truth_state=TruthState.REPRESENTATIVE,
        )

        # 2. Equipment Setup (P-101, E-101..E-105, V-101, V-102, F-101, C-101)
        eq_p101 = EquipmentModel(
            equipment_id="P-101",
            equipment_type=EquipmentType.PUMP,
            name="Crude Charge Pump",
            unit_id="CDU-100",
            provenance=prov,
            truth_state=TruthState.REPRESENTATIVE,
        )

        # Heat Exchangers E-101 .. E-105 mapped to FOUL-X E01 .. E05
        foulx_mapping = {
            "E-101": {"foulx_id": "E01", "service": "Heavy Naphtha Preheat", "tube_fluid": "Crude Feed", "shell_fluid": "Heavy Naphtha"},
            "E-102": {"foulx_id": "E02", "service": "Kerosene Preheat", "tube_fluid": "Crude Feed", "shell_fluid": "Kerosene"},
            "E-103": {"foulx_id": "E03", "service": "Light Diesel Preheat", "tube_fluid": "Crude Feed", "shell_fluid": "Light Diesel"},
            "E-104": {"foulx_id": "E04", "service": "LVGO Preheat", "tube_fluid": "Crude Feed", "shell_fluid": "LVGO"},
            "E-105": {"foulx_id": "E05", "service": "Heavy Diesel Preheat", "tube_fluid": "Crude Feed", "shell_fluid": "Heavy Diesel"},
        }

        hxs = {}
        for eq_id, info in foulx_mapping.items():
            hxs[eq_id] = HeatExchangerModel(
                equipment_id=eq_id,
                equipment_type=EquipmentType.HEAT_EXCHANGER,
                name=f"{eq_id} {info['service']} Exchanger",
                unit_id="CDU-100",
                area=120.0,
                tube_count=450,
                tube_diameter=0.025,
                tube_length=6.0,
                material="Carbon Steel",
                fouling_reference={
                    "foulx_asset_id": info["foulx_id"],
                    "dataset_limitation": "No pressure, No ΔP, No cleaning timestamps, No explicit composition in raw CSV",
                },
                provenance=prov,
                truth_state=TruthState.REPRESENTATIVE,
            )

        eq_v101 = EquipmentModel(
            equipment_id="V-101",
            equipment_type=EquipmentType.SEPARATOR,
            name="Desalter Vessel V-101",
            unit_id="CDU-100",
            provenance=prov,
            truth_state=TruthState.REPRESENTATIVE,
        )

        eq_v102 = EquipmentModel(
            equipment_id="V-102",
            equipment_type=EquipmentType.SEPARATOR,
            name="Pre-Flash Vessel V-102",
            unit_id="CDU-100",
            provenance=prov,
            truth_state=TruthState.REPRESENTATIVE,
        )

        eq_f101 = EquipmentModel(
            equipment_id="F-101",
            equipment_type=EquipmentType.FURNACE,
            name="Crude Charge Heater F-101",
            unit_id="CDU-100",
            provenance=prov,
            truth_state=TruthState.REPRESENTATIVE,
        )

        eq_c101 = EquipmentModel(
            equipment_id="C-101",
            equipment_type=EquipmentType.DISTILLATION_COLUMN,
            name="Atmospheric Crude Column C-101",
            unit_id="CDU-100",
            provenance=prov,
            truth_state=TruthState.REPRESENTATIVE,
        )

        # Register equipment
        model.equipment["P-101"] = eq_p101
        for eq_id, hx in hxs.items():
            model.equipment[eq_id] = hx
        model.equipment["V-101"] = eq_v101
        model.equipment["V-102"] = eq_v102
        model.equipment["F-101"] = eq_f101
        model.equipment["C-101"] = eq_c101

        unit_cdu.equipment_ids = list(model.equipment.keys())
        model.units["CDU-100"] = unit_cdu

        # 3. Process Streams
        stream_sequence = [
            ("S-01", "Raw Crude Feed", None, "P-101"),
            ("S-02", "Crude Discharge to E-101", "P-101", "E-101"),
            ("S-03", "Crude E-101 to E-102", "E-101", "E-102"),
            ("S-04", "Crude E-102 to E-103", "E-102", "E-103"),
            ("S-05", "Crude E-103 to V-101", "E-103", "V-101"),
            ("S-06", "Desalted Crude to E-104", "V-101", "E-104"),
            ("S-07", "Crude E-104 to E-105", "E-104", "E-105"),
            ("S-08", "Crude E-105 to V-102", "E-105", "V-102"),
            ("S-09", "Flashed Crude to F-101", "V-102", "F-101"),
            ("S-10", "Hot Feed to C-101 Column", "F-101", "C-101"),
        ]

        for s_id, s_name, src, dst in stream_sequence:
            st = ProcessStream(
                stream_id=s_id,
                name=s_name,
                source_equipment_id=src,
                destination_equipment_id=dst,
                phase=StreamPhase.LIQUID if s_id != "S-10" else StreamPhase.TWO_PHASE,
                temperature=150.0 if s_id == "S-04" else None,
                pressure=None,  # Explicitly UNAVAILABLE per dataset limits
                mass_flow=50.0,
                volumetric_flow=None,
                provenance=prov,
                truth_state=TruthState.REPRESENTATIVE,
            )
            model.streams[s_id] = st
            if src and src in model.equipment:
                model.equipment[src].outlet_stream_ids.append(s_id)
            if dst and dst in model.equipment:
                model.equipment[dst].inlet_stream_ids.append(s_id)

        # 4. Measurement Bindings
        meas_e102 = MeasurementBinding(
            binding_id="mb-e102-temp-in",
            measurement_id="T_in_c",
            entity_id="E-102",
            variable="cold_inlet_temperature",
            unit="°C",
            timestamp=eval_timestamp,
            source="HISTORIAN_TELEMETRY",
            provenance=prov,
            truth_state=TruthState.OBSERVED,
        )
        model.measurements.append(meas_e102)
        model.equipment["E-102"].measurements.append(meas_e102)

        # Source immutability verification after model build
        h_after = hashlib.sha256(data_path.read_bytes()).hexdigest()
        if h_before != h_after:
            raise ProcessSourceMutation("Raw dataset was mutated during Stage 11 process model construction!")

        # Build Graph & compute hash
        graph = GraphEngine.build_graph_from_model(model)
        return model, graph
