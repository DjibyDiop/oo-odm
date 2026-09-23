import time
import json
from typing import Dict, Any, List
from enum import Enum, auto
from meo.ontology import Bloc, Liaison, Structure
from meo.meo_engine import Espace

class OIRType(Enum):
    COMPUTE_DYNAMICS = "COMPUTE_DYNAMICS"
    ANALYZE_MEMORY = "ANALYZE_MEMORY"
    ANALYZE_PATTERNS = "ANALYZE_PATTERNS"
    EVALUATE_RULES = "EVALUATE_RULES"
    UPDATE_STATE = "UPDATE_STATE"
    EXPLORE_SCENARIO = "EXPLORE_SCENARIO"
    VALIDATE_ONTOLOGY = "VALIDATE_ONTOLOGY"
    RECORD_TRAJECTORY = "RECORD_TRAJECTORY"
    EXECUTE_DPLUS_OP = "EXECUTE_DPLUS_OP"
    VALIDATE_GRAMMAR = "VALIDATE_GRAMMAR"

class OIRSerializer:
    """
    Sérialiseur pur (externe à l'Ontologie MEO) pour convertir 
    l'Espace vers l'OIR et inversement.
    """
    @staticmethod
    def serialize_bloc(bloc: Bloc) -> Dict[str, Any]:
        return {
            "id": bloc.id,
            "name": bloc.name,
            "forme": bloc.forme,
            "caracteristiques": bloc.caracteristiques
        }
        
    @staticmethod
    def deserialize_bloc(data: Dict[str, Any]) -> Bloc:
        b = Bloc(data["name"], data["forme"], data["caracteristiques"])
        b.id = data["id"]
        return b

    @staticmethod
    def serialize_liaison(liaison: Liaison) -> Dict[str, Any]:
        return {
            "id": liaison.id,
            "source_id": liaison.source_id,
            "target_id": liaison.target_id,
            "nature": liaison.nature,
            "oriente": liaison.oriente
        }

    @staticmethod
    def deserialize_liaison(data: Dict[str, Any]) -> Liaison:
        l = Liaison(data["source_id"], data["target_id"], data["nature"], data["oriente"])
        l.id = data["id"]
        return l

    @staticmethod
    def serialize_structure(structure: Structure) -> Dict[str, Any]:
        return {
            "id": structure.id,
            "name": structure.name,
            "blocs": [OIRSerializer.serialize_bloc(b) for b in structure.blocs.values()],
            "liaisons": [OIRSerializer.serialize_liaison(l) for l in structure.liaisons]
        }

    @staticmethod
    def deserialize_structure(data: Dict[str, Any]) -> Structure:
        s = Structure(data["name"])
        s.id = data["id"]
        for b_data in data["blocs"]:
            s.add_bloc(OIRSerializer.deserialize_bloc(b_data))
        for l_data in data["liaisons"]:
            s.add_liaison(OIRSerializer.deserialize_liaison(l_data))
        return s

    @staticmethod
    def serialize_espace(espace: Espace) -> Dict[str, Any]:
        return {
            "blocs_libres": [OIRSerializer.serialize_bloc(b) for b in espace.blocs_libres.values()],
            "structures": [OIRSerializer.serialize_structure(s) for s in espace.structures],
            "global_properties": espace.global_properties
        }

    @staticmethod
    def deserialize_espace(data: Dict[str, Any]) -> Espace:
        e = Espace()
        e.global_properties = data.get("global_properties", {})
        for b_data in data.get("blocs_libres", []):
            e.add_bloc_libre(OIRSerializer.deserialize_bloc(b_data))
        for s_data in data.get("structures", []):
            e.add_structure(OIRSerializer.deserialize_structure(s_data))
        return e


class OIRInstruction:
    """
    Organic Intermediate Representation (OIR)
    Le langage intermédiaire commun compris par tous les moteurs d'OMX.
    """
    def __init__(self, op_type: OIRType, payload: Dict[str, Any], origin: str = "O-D+", parameters: Dict[str, Any] = None):
        self.op_type = op_type
        self.payload = payload
        self.parameters = parameters or {}
        self.origin = origin
        self.timestamp = int(time.time())
        import uuid
        self.message_id = str(uuid.uuid4())
        
    def to_json(self) -> str:
        """
        Exporte l'instruction complète au format JSON strict.
        """
        # Si le payload contient un Espace, on le sérialise
        encoded_payload = self.payload.copy()
        if "espace" in encoded_payload and isinstance(encoded_payload["espace"], Espace):
            encoded_payload["espace"] = OIRSerializer.serialize_espace(encoded_payload["espace"])
            
        envelope = {
            "oir_version": "1.0",
            "message_type": "instruction",
            "metadata": {
                "origin": self.origin,
                "timestamp": self.timestamp,
                "message_id": self.message_id,
                "schema": "oir-1.0"
            },
            "instruction": {
                "operation": self.op_type.value,
                "parameters": self.parameters
            },
            "payload": encoded_payload
        }
        return json.dumps(envelope, ensure_ascii=False, indent=2)
        
    @classmethod
    def from_json(cls, json_str: str) -> 'OIRInstruction':
        """
        Reconstruit une OIRInstruction à partir d'un JSON brut reçu (ex: depuis Rust/C++).
        """
        data = json.loads(json_str)
        op_type = OIRType(data["instruction"]["operation"])
        parameters = data["instruction"].get("parameters", {})
        
        payload = data.get("payload", {})
        # Si on détecte qu'il s'agit d'un espace sérialisé, on le reconstruit
        if "espace" in payload and isinstance(payload["espace"], dict) and "blocs_libres" in payload["espace"]:
            payload["espace"] = OIRSerializer.deserialize_espace(payload["espace"])
            
        inst = cls(op_type, payload, origin=data.get("metadata", {}).get("origin", "UNKNOWN"), parameters=parameters)
        inst.timestamp = data.get("metadata", {}).get("timestamp", int(time.time()))
        inst.message_id = data.get("metadata", {}).get("message_id", "UNKNOWN")
        return inst

    def __repr__(self):
        return f"OIRInstruction(type={self.op_type.value}, origin={self.origin}, id={self.message_id})"
