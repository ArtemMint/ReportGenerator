import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from app.core.logging import get_logger
from app.schemas.report import OutputConfig
from .abstract import AbstractOutput

logger = get_logger(__name__)


class JSONOutput(AbstractOutput):
    def __init__(self, config: OutputConfig, report_id: str) -> None:
        self._config = config
        self._report_id = report_id


    async def write(self, data: pd.DataFrame) -> dict:
        filename = f"report_{self._report_id}.json"
        path = Path(self._config.path) / filename

        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total": len(data),
            "employees": data.to_dict(orient="records"),
        }

        await asyncio.to_thread(self._write_file, path, payload)
        return path

    @staticmethod
    def _write_file(path: Path, payload: dict) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
