import asyncio
import json
from datetime import datetime, timezone

import pandas as pd

from app.core.logging import get_logger
from app.schemas.report import OutputConfig
from .abstract import AbstractOutput

logger = get_logger(__name__)


class JSONOutput(AbstractOutput):
    def __init__(self, config: OutputConfig) -> None:
        self._config = config

    async def write(self, data: pd.DataFrame) -> dict:
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total": len(data),
            "employees": data.to_dict(orient="records"),
        }

        if self._config.path:
            await asyncio.to_thread(self._write_file, payload)
            logger.info("json_output.written_to_file", path=self._config.path)

        logger.info("json_output.done", total=len(data))
        return payload

    def _write_file(self, payload: dict) -> None:
        with open(self._config.path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
