from dataclasses import dataclass
from typing import Any, Dict, List, Union

@dataclass
class Stats:
    num_null_entries: int
    type: str
@dataclass
class NumericStats(Stats):
    min: float
    max: float
    mean: float
    std: float
    quantile_25: float
    quantile_50: float
    quantile_75: float
@dataclass
class CategoricalStats(Stats):
    num_unique_entries: int
    most_common_entries: Dict[str, int]
@dataclass
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
