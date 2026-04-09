from .abstract import AbstractOutput


class CSVOutput(AbstractOutput):

    def write(self, data: list[dict]):
        raise NotImplemented("CSVOutput.write is not implemented yet")