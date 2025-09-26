"""Defines the YAML specifications"""
import datetime
from dataclasses import dataclass

import semver

@dataclass
class Approver():
    Name: str
    Email: str
    Date: datetime.date

@dataclass
class Metadata():
    Proposed: datetime.date
    Adoption: datetime.date | None
    Modified: datetime.date | None
    Version: semver.Version
    Status: str
    Approvers: list[Approver]

@dataclass
class SpecID():
    ID: str

@dataclass
class Capability():
    Title: str
    Description: str
    Actions: list[SpecID]

@dataclass
class Domain():
    Title: str
    Description: str
    Capabilities: list[SpecID | Capability]

@dataclass
class Reference():
    Name: str
    Link: str
    Comment: str

@dataclass
class ActionSpec():
    ID: str
    Title: str
    Description: str
    ImplementationTypes: list[str | None]
    References: list[Reference | None]
    Notes: list[str | None]

@dataclass
class CapabilitySpec():
    ID: str

@dataclass
class DomainSpec():
    ID: str

@dataclass
class ProfileSpec():
    ID: str
    Title: str
    Description: str
    Domains: list[SpecID | Domain]

@dataclass
class Specification():
    Metadata: Metadata
    Specification: ProfileSpec | DomainSpec | CapabilitySpec | ActionSpec