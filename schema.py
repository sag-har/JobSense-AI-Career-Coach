from pydantic import BaseModel
from typing import List


class CareerReport(BaseModel):
    match_score: int                     # 0-100
    matched_skills: List[str]            # skills you have that JD wants
    missing_skills: List[str]            # your gaps
    strengths: List[str]                 # 3 things to highlight in interview
    rewritten_bullets: List[str]         # 3 improved CV bullet points
    interview_talking_points: List[str]  # 5 concrete things to say