from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


DiagramConnectionInferenceMode = Literal["none", "auto", "strict"]


@dataclass(frozen=True)
class EntityTypeInfo:
    artifact_type: str
    prefix: str
    layer_dir: str
    subdir: str
    archimate_layer: str
    archimate_element_type: str


@dataclass(frozen=True)
class ConnectionTypeInfo:
    artifact_type: str
    conn_lang: str
    conn_dir: str
    archimate_relationship_type: str | None = None


ENTITY_TYPES: dict[str, EntityTypeInfo] = {
    "stakeholder": EntityTypeInfo("stakeholder", "STK", "motivation", "stakeholders", "Motivation", "Stakeholder"),
    "driver": EntityTypeInfo("driver", "DRV", "motivation", "drivers", "Motivation", "Driver"),
    "assessment": EntityTypeInfo("assessment", "ASS", "motivation", "assessments", "Motivation", "Assessment"),
    "goal": EntityTypeInfo("goal", "GOL", "motivation", "goals", "Motivation", "Goal"),
    "outcome": EntityTypeInfo("outcome", "OUT", "motivation", "outcomes", "Motivation", "Outcome"),
    "principle": EntityTypeInfo("principle", "PRI", "motivation", "principles", "Motivation", "Principle"),
    "requirement": EntityTypeInfo("requirement", "REQ", "motivation", "requirements", "Motivation", "Requirement"),
    "architecture-constraint": EntityTypeInfo("architecture-constraint", "CST", "motivation", "constraints", "Motivation", "Constraint"),
    "meaning": EntityTypeInfo("meaning", "MEA", "motivation", "meanings", "Motivation", "Meaning"),
    "value": EntityTypeInfo("value", "VAL", "motivation", "values", "Motivation", "Value"),
    "capability": EntityTypeInfo("capability", "CAP", "strategy", "capabilities", "Strategy", "Capability"),
    "value-stream": EntityTypeInfo("value-stream", "VS", "strategy", "value-streams", "Strategy", "ValueStream"),
    "resource": EntityTypeInfo("resource", "RES", "strategy", "resources", "Strategy", "Resource"),
    "course-of-action": EntityTypeInfo("course-of-action", "COA", "strategy", "courses-of-action", "Strategy", "CourseOfAction"),
    "business-actor": EntityTypeInfo("business-actor", "ACT", "business", "actors", "Business", "BusinessActor"),
    "business-role": EntityTypeInfo("business-role", "ROL", "business", "roles", "Business", "BusinessRole"),
    "business-collaboration": EntityTypeInfo("business-collaboration", "BCO", "business", "collaborations", "Business", "BusinessCollaboration"),
    "business-interface": EntityTypeInfo("business-interface", "BIF", "business", "interfaces", "Business", "BusinessInterface"),
    "business-process": EntityTypeInfo("business-process", "BPR", "business", "processes", "Business", "BusinessProcess"),
    "business-function": EntityTypeInfo("business-function", "BFN", "business", "functions", "Business", "BusinessFunction"),
    "business-interaction": EntityTypeInfo("business-interaction", "BIA", "business", "interactions", "Business", "BusinessInteraction"),
    "business-event": EntityTypeInfo("business-event", "BEV", "business", "events", "Business", "BusinessEvent"),
    "business-service": EntityTypeInfo("business-service", "BSV", "business", "services", "Business", "BusinessService"),
    "business-object": EntityTypeInfo("business-object", "BOB", "business", "objects", "Business", "BusinessObject"),
    "contract": EntityTypeInfo("contract", "CTR", "business", "contracts", "Business", "Contract"),
    "representation": EntityTypeInfo("representation", "RPR", "business", "representations", "Business", "Representation"),
    "product": EntityTypeInfo("product", "PRD", "business", "products", "Business", "Product"),
    "application-component": EntityTypeInfo("application-component", "APP", "application", "components", "Application", "ApplicationComponent"),
    "application-collaboration": EntityTypeInfo("application-collaboration", "ACO", "application", "collaborations", "Application", "ApplicationCollaboration"),
    "application-interface": EntityTypeInfo("application-interface", "AIF", "application", "interfaces", "Application", "ApplicationInterface"),
    "application-function": EntityTypeInfo("application-function", "AFN", "application", "functions", "Application", "ApplicationFunction"),
    "application-interaction": EntityTypeInfo("application-interaction", "AIA", "application", "interactions", "Application", "ApplicationInteraction"),
    "application-process": EntityTypeInfo("application-process", "APR", "application", "processes", "Application", "ApplicationProcess"),
    "application-event": EntityTypeInfo("application-event", "AEV", "application", "events", "Application", "ApplicationEvent"),
    "application-service": EntityTypeInfo("application-service", "ASV", "application", "services", "Application", "ApplicationService"),
    "data-object": EntityTypeInfo("data-object", "DOB", "application", "data-objects", "Application", "DataObject"),
    "technology-node": EntityTypeInfo("technology-node", "NOD", "technology", "nodes", "Technology", "Node"),
    "device": EntityTypeInfo("device", "DEV", "technology", "devices", "Technology", "Device"),
    "system-software": EntityTypeInfo("system-software", "SSW", "technology", "system-software", "Technology", "SystemSoftware"),
    "technology-collaboration": EntityTypeInfo("technology-collaboration", "TCO", "technology", "collaborations", "Technology", "TechnologyCollaboration"),
    "technology-interface": EntityTypeInfo("technology-interface", "TIF", "technology", "interfaces", "Technology", "TechnologyInterface"),
    "path": EntityTypeInfo("path", "PTH", "technology", "paths", "Technology", "Path"),
    "communication-network": EntityTypeInfo("communication-network", "NET", "technology", "networks", "Technology", "CommunicationNetwork"),
    "technology-function": EntityTypeInfo("technology-function", "TFN", "technology", "functions", "Technology", "TechnologyFunction"),
    "technology-process": EntityTypeInfo("technology-process", "TPR", "technology", "processes", "Technology", "TechnologyProcess"),
    "technology-interaction": EntityTypeInfo("technology-interaction", "TIA", "technology", "interactions", "Technology", "TechnologyInteraction"),
    "technology-event": EntityTypeInfo("technology-event", "TEV", "technology", "events", "Technology", "TechnologyEvent"),
    "technology-service": EntityTypeInfo("technology-service", "TSV", "technology", "services", "Technology", "TechnologyService"),
    "artifact": EntityTypeInfo("artifact", "ART", "technology", "artifacts", "Technology", "Artifact"),
    "equipment": EntityTypeInfo("equipment", "EQP", "physical", "equipment", "Physical", "Equipment"),
    "facility": EntityTypeInfo("facility", "FAC", "physical", "facilities", "Physical", "Facility"),
    "distribution-network": EntityTypeInfo("distribution-network", "DIS", "physical", "distribution-networks", "Physical", "DistributionNetwork"),
    "material": EntityTypeInfo("material", "MAT", "physical", "materials", "Physical", "Material"),
    "work-package": EntityTypeInfo("work-package", "WP", "implementation", "work-packages", "Implementation", "WorkPackage"),
    "deliverable": EntityTypeInfo("deliverable", "DEL", "implementation", "deliverables", "Implementation", "Deliverable"),
    "implementation-event": EntityTypeInfo("implementation-event", "IEV", "implementation", "events", "Implementation", "ImplementationEvent"),
    "plateau": EntityTypeInfo("plateau", "PLT", "implementation", "plateaus", "Implementation", "Plateau"),
    "gap": EntityTypeInfo("gap", "GAP", "implementation", "gaps", "Implementation", "Gap"),
}


CONNECTION_TYPES: dict[str, ConnectionTypeInfo] = {
    "archimate-composition": ConnectionTypeInfo("archimate-composition", "archimate", "composition", "Composition"),
    "archimate-aggregation": ConnectionTypeInfo("archimate-aggregation", "archimate", "aggregation", "Aggregation"),
    "archimate-assignment": ConnectionTypeInfo("archimate-assignment", "archimate", "assignment", "Assignment"),
    "archimate-realization": ConnectionTypeInfo("archimate-realization", "archimate", "realization", "Realization"),
    "archimate-serving": ConnectionTypeInfo("archimate-serving", "archimate", "serving", "Serving"),
    "archimate-access": ConnectionTypeInfo("archimate-access", "archimate", "access", "Access"),
    "archimate-influence": ConnectionTypeInfo("archimate-influence", "archimate", "influence", "Influence"),
    "archimate-association": ConnectionTypeInfo("archimate-association", "archimate", "association", "Association"),
    "archimate-specialization": ConnectionTypeInfo("archimate-specialization", "archimate", "specialization", "Specialization"),
    "archimate-flow": ConnectionTypeInfo("archimate-flow", "archimate", "flow", "Flow"),
    "archimate-triggering": ConnectionTypeInfo("archimate-triggering", "archimate", "triggering", "Triggering"),
    "er-one-to-many": ConnectionTypeInfo("er-one-to-many", "er", "one-to-many"),
    "er-many-to-many": ConnectionTypeInfo("er-many-to-many", "er", "many-to-many"),
    "er-one-to-one": ConnectionTypeInfo("er-one-to-one", "er", "one-to-one"),
    "sequence-synchronous": ConnectionTypeInfo("sequence-synchronous", "sequence", "synchronous"),
    "sequence-asynchronous": ConnectionTypeInfo("sequence-asynchronous", "sequence", "asynchronous"),
    "sequence-return": ConnectionTypeInfo("sequence-return", "sequence", "return"),
    "sequence-create": ConnectionTypeInfo("sequence-create", "sequence", "create"),
    "sequence-destroy": ConnectionTypeInfo("sequence-destroy", "sequence", "destroy"),
    "activity-sequence-flow": ConnectionTypeInfo("activity-sequence-flow", "activity", "sequence-flow"),
    "activity-decision": ConnectionTypeInfo("activity-decision", "activity", "decision"),
    "activity-message-flow": ConnectionTypeInfo("activity-message-flow", "activity", "message-flow"),
    "activity-data-association": ConnectionTypeInfo("activity-data-association", "activity", "data-association"),
    "usecase-include": ConnectionTypeInfo("usecase-include", "usecase", "include"),
    "usecase-extend": ConnectionTypeInfo("usecase-extend", "usecase", "extend"),
    "usecase-association": ConnectionTypeInfo("usecase-association", "usecase", "actor-association"),
    "usecase-generalization": ConnectionTypeInfo("usecase-generalization", "usecase", "generalization"),
}


ARCHIMATE_STEREOTYPE_TO_CONNECTION_TYPE: dict[str, str] = {
    "composition": "archimate-composition",
    "aggregation": "archimate-aggregation",
    "assignment": "archimate-assignment",
    "realization": "archimate-realization",
    "serving": "archimate-serving",
    "access": "archimate-access",
    "influence": "archimate-influence",
    "association": "archimate-association",
    "specialization": "archimate-specialization",
    "flow": "archimate-flow",
    "triggering": "archimate-triggering",
}
