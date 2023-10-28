from typing import Any, Dict, List, Union
from pydantic import BaseModel

class Stats(BaseModel):
    num_null_entries: int
    type: str

class NumericStats(Stats):
    min: float
    max: float
    mean: float
    std: float
    quantile_25: float
    quantile_50: float
    quantile_75: float

class CategoricalStats(Stats):
    num_unique_entries: int
    most_common_entries: Dict[str, int]

class DateStats(CategoricalStats):
    earliest: str
    latest: str

class MatrixProfile(BaseModel):
    matrix_stats: NumericStats

class TabularProfile(BaseModel):
    col_name: str
    concept: str
    unit: str
    description: str
    dkg_groundings: List[List[str]]
    column_stats: Union[NumericStats, DateStats, CategoricalStats]

class BaseDataCard(BaseModel):
    DESCRIPTION: str
    AUTHOR_NAME: str
    AUTHOR_EMAIL: str
    DATE: str
    PROVENANCE: str
    SENSITIVITY: str
    LICENSE: str
    DATASET_TYPE: str

class MatrixDataCard(BaseDataCard):
    DATA_PROFILING_RESULT: MatrixProfile
    EXAMPLES: List[float]
    CELL_INTERPRETATION: str

class TabularDataCard(BaseDataCard):
    SCHEMA: List[str]
    DATA_PROFILING_RESULT: Dict[str, TabularProfile]
    EXAMPLES: Dict[str, Any]

class ModelCard(BaseModel):
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
