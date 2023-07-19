from dataclasses import dataclass
from typing import Any, Dict, List, Union
from pydantic import Field, BaseModel

class Stats(BaseModel):
    num_null_entries: int
    type: str

    class Config:
        allow_population_by_field_name = True
class NumericStats(Stats):
    min: float
    max: float
    mean: float
    std: float
    quantile_25: float = Field(alias='25%')
    quantile_50: float = Field(alias='50%')
    quantile_75: float = Field(alias='75%')

    class Config:
        allow_population_by_field_name = True
class CategoricalStats(Stats):
    num_unique_entries: int
    most_common_entries: Dict[str, int]
class DateStats(CategoricalStats):
    earliest: str
    latest: str

@dataclass
class MatrixProfile:
    matrix_stats: NumericStats
@dataclass
class TabularProfile:
    col_name: str
    concept: str
    unit: str
    description: str
    dkg_groundings: List[List[str]]
    column_stats: Union[CategoricalStats, NumericStats, DateStats]

@dataclass
class BaseDataCard:
    DESCRIPTION: str
    AUTHOR_NAME: str
    AUTHOR_EMAIL: str
    DATE: str
    PROVENANCE: str
    SENSITIVITY: str
    LICENSE: str
    DATASET_TYPE: str
@dataclass
class MatrixDataCard(BaseDataCard):
    DATA_PROFILING_RESULT: MatrixProfile
    EXAMPLES: List[float]
    CELL_INTERPRETATION: str
@dataclass
class TabularDataCard(BaseDataCard):
    SCHEMA: List[str]
    DATA_PROFILING_RESULT: Dict[str, TabularProfile]
    EXAMPLES: Dict[str, Any]

@dataclass
class ModelCard:
    DESCRIPTION: str
    AUTHOR_INST: str
    AUTHOR_AUTHOR: str
    AUTHOR_EMAIL: str
    DATE: str
    SCHEMA: str
    PROVENANCE: str
    DATASET: str
    COMPLEXITY: str
    USAGE: str
    LICENSE: str
