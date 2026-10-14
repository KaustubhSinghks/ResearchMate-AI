from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # "document" | "author" | "tag"


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str  # "authored" | "tagged" | "cites" | "similar"
    weight: float = 1.0


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
