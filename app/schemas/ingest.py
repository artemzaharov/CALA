from pydantic import BaseModel


class IngestRequest(BaseModel):
    text: str


# A single node in the knowledge graph (e.g. a person, company, or location).
class Node(BaseModel):
    name: str
    type: str  # "Person" | "Company" | "Location"


# A directed relationship between two nodes.
class Relation(BaseModel):
    from_: str  # name of the source node
    to: str     # name of the target node
    type: str   # e.g. "FOUNDED", "WORKS_AT", "LOCATED_IN"


# The structured data the LLM returns after entity extraction.
class ExtractedGraph(BaseModel):
    nodes: list[Node]
    relations: list[Relation]


class IngestResponse(BaseModel):
    nodes_created: int
    relations_created: int
