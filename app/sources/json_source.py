import io

import aiofiles
import pandas as pd

from .abstract import AbstractSource


class JSONSource(AbstractSource):
    async def read(self) -> pd.DataFrame:
        """Read JSON data from a file path or raw content."""
        async with aiofiles.open(self.source, mode='r') as f:
            content = await f.read()

        # Use pandas to read JSON content from a string
        df = pd.read_json(io.StringIO(content))
        return df
