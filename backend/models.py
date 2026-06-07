# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
from enum import Enum
from typing import Optional
from pydantic import BaseModel

# MODELS -------------------------------------------------------------------------------------------------------------------------------------------|

# (1) Risk Levels
class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

# (2) Ecosystem
class EcosystemType(str, Enum):
    PIP = "pip"
    NPM = "npm"
    CARGO = "cargo"
    GO = "go"

# (3) CVE 
class CVE(BaseModel):
    id: str
    description: str
    severity: str
    cvss: Optional[float] = None
    fixed_version: Optional[str] = None

# (4) Node
class Node(BaseModel):
    id: str
    version: str
    ecosystem: str
    risk: RiskLevel = RiskLevel.NONE
    cves: list[CVE] = []
    is_direct: bool = False

# (5) Edge
class Edge(BaseModel):
    source: str
    target: str

# (6) Graph Response
class GraphResponse(BaseModel):
    nodes: list[Node]
    edges: list[Edge]
    total: int
    high_cve_count: int
    medium_cve_count: int
    clean_count: int
