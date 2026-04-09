import io

import aiofiles
import pandas as pd

from .abstract import AbstractSource


class CSVSource(AbstractSource):
    async def read(self) -> pd.DataFrame:
        """Read CSV data from a file path or raw content."""
        async with aiofiles.open(self.source, mode='r') as f:
            content = await f.read()

        # Use pandas to read CSV content from a string
        df = pd.read_csv(io.StringIO(content))
        return df
