from app.algorithms.code_repair_agent import CodeRepairAgent


class ExecutionAgent:
    def __init__(self) -> None:
        self.repair = CodeRepairAgent()

    def prepare_payload(self, text: str) -> str:
        return self.repair.sanitize(text)
