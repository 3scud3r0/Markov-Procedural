"""Shared domain documents and output artifacts."""
from dataclasses import dataclass,field


@dataclass(frozen=True)
class Document:
    kind: str
    value: object
    metadata: dict=field(default_factory=dict)

    def to_data(self):
        value=self.value.to_data() if hasattr(self.value,'to_data') else self.value
        return {'schema':'markovjunior.document/1','kind':self.kind,'metadata':self.metadata,'value':value}


@dataclass(frozen=True)
class Artifact:
    filename: str
    content: str | bytes
    media_type: str

    def bytes(self):
        return self.content.encode('utf-8') if isinstance(self.content,str) else self.content
