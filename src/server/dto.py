from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class Grade(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

@dataclass
class StudentDto:
    name: str
    school: str
    gender: Gender
    academicPerformance: Grade
    behavioralPerformance: Grade
    comments: str
    friend1: str
    friend2: str
    friend3: str
    friend4: str
    notWith: Optional[str] = None
    clusterId: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict):
        data['gender'] = Gender(data['gender'])
        data['academicPerformance'] = Grade(data['academicPerformance'])
        data['behavioralPerformance'] = Grade(data['behavioralPerformance'])
        return cls(**data)

@dataclass
class ClassSummaryDto:
    classNumber: int
    studentsCount: int
    malesCount: int
    averageAcademicPerformance: float
    averageBehaviouralPerformance: float
    withoutFriends: int
    unwantedMatches: int 