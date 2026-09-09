from typing import Protocol
from packages.security.redaction import redact
class Provider(Protocol):
    def complete(self,prompt:str)->str: ...
class ModelGateway:
    def __init__(self,providers:list[Provider],max_chars:int=20000)->None:
        if not providers: raise ValueError('at least one provider required')
        self.providers=providers; self.max_chars=max_chars
    def complete(self,prompt:str)->str:
        safe=redact(prompt)[:self.max_chars]
        errors=[]
        for provider in self.providers:
            try: return provider.complete(safe)
            except Exception as exc: errors.append(type(exc).__name__)
        raise RuntimeError('all model providers failed: '+','.join(errors))
