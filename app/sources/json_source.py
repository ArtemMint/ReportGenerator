import io

import aiofiles
import pandas as pd

from .abstract import AbstractSource


class JSONSource(AbstractSource):
    async def read(self) -> pd.DataFrame:
        """Read JSON data from a file path or raw content."""
        if self.source.startswith("file://"):
            file_path = self.source[7:]  # Remove "file://" prefix
            async with aiofiles.open(file_path, mode='r') as f:
                content = await f.read()
        else:
            content = self.source

        # Use pandas to read JSON content from a string
        df = pd.read_json(io.StringIO(content))
        return df
