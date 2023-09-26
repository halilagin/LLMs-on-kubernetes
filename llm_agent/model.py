import dataclasses 
from dataclasses import dataclass
from typing import List, Dict





@dataclass
class Query:
    query: str


@dataclass
class Answer:
    question: str
    sources: List[str]
    answer: str
    llm: str


