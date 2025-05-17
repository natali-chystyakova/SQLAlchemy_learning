from datetime import datetime

from pydantic import BaseModel

# from models import Workload #noqa
from src.enums import Workload  # перечисления держим в тодельном файле


class WorkersAddDTO(BaseModel):
    username: str


class WorkersDTO(WorkersAddDTO):
    id: int


class ResumesAddDTO(BaseModel):
    title: str
    compensation: int | None
    workload: Workload
    worker_id: int


class ResumesDTO(ResumesAddDTO):
    id: int
    created_at: datetime
    updated_at: datetime


class ResumesRelDTO(ResumesDTO):
    worker: "WorkersDTO"


class WorkersRelDTO(WorkersDTO):
    resumes: list["ResumesDTO"]


class WorkloadAvgCompensationDTO(BaseModel):
    workload: Workload
    avg_compensation: int


class VacanciesAddDTO(BaseModel):
    title: str
    compensation: int | None


class VacanciesDTO(VacanciesAddDTO):
    id: int


class ResumesRelVacanciesRepliedDTO(ResumesDTO):
    worker: "WorkersDTO"
    vacancies_replied: list["VacanciesDTO"]
