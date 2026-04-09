import io

import aiofiles
import pandas as pd

from .abstract import AbstractSource


class CSVSource(AbstractSource):
    async def read(self) -> pd.DataFrame:
        """Read CSV data from a file path or raw content."""
        if self.source.startswith("file://"):
            file_path = self.source[7:]  # Remove "file://" prefix
            async with aiofiles.open(file_path, mode='r') as f:
                content = await f.read()
        else:
            content = self.source

        # Use pandas to read CSV content from a string
        df = pd.read_csv(io.StringIO(content))
        return df
