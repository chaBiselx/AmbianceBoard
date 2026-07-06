from dataclasses import dataclass


@dataclass
class SupportContactDto:
    email: str
    subject: str
    message: str
