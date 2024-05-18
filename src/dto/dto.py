from dataclasses import dataclass

@dataclass
class FiltersParser:
    data_start: str = '1999-01-01'
    data_end: str = '1999-01-01'
    date_join: bool = True
    status: bool = True
    user_id: int = 1