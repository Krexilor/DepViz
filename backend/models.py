# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
from enum import Enum
from typing import Optional
from pydantic import BaseModel

# RISK LEVEL ---------------------------------------------------------------------------------------------------------------------------------------|
class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

# ECOSYSTEM ----------------------------------------------------------------------------------------------------------------------------------------|
class EcosystemType(str, Enum):
    PIP = "pip"
    NPM = "npm"
    CARGO = "cargo"
    GO = "go"
    GEM = "gem"

# CVE ----------------------------------------------------------------------------------------------------------------------------------------------|
class CVE(BaseModel):
    id: str
    description: str
    severity: str
    cvss: Optional[float] = None
    fixed_version: Optional[str]  = None

# NODE ---------------------------------------------------------------------------------------------------------------------------------------------|
class Node(BaseModel):
    id: str
    version: str
    ecosystem: str
    risk: RiskLevel = RiskLevel.NONE
    cves: list[CVE] = []
    is_direct: bool = False

# EDGE ---------------------------------------------------------------------------------------------------------------------------------------------|
class Edge(BaseModel):
    source: str
    target: str

# GRAPH RESPONSE -----------------------------------------------------------------------------------------------------------------------------------|
class GraphResponse(BaseModel):
    nodes: list[Node]
    edges: list[Edge]
    total: int
    high_cve_count: int
    medium_cve_count: int
    clean_count: int
