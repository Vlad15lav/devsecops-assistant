from src.application.models.base_agent_models import BaseAgentOutput
from typing import List, Dict, Any, Optional


class SQLAgentOutput(BaseAgentOutput):
    result: str
    returned_rows: Optional[List[Dict[str, Any]]] = None
