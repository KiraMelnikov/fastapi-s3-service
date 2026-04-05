from typing import Protocol


class UploadMeta(Protocol):
    """ Protocol for upload metadata """

    write_mode_per_day: str
