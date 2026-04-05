from typing import final

from pydantic import dataclasses


@final
@dataclasses.dataclass(frozen=True)
class Sources:
    cyber_security_vulnerabilities = "cyber-security-vulnerabilities"


sources = Sources()
