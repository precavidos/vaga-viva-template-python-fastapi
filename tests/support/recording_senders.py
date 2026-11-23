from dataclasses import dataclass, field


@dataclass(frozen=True)
class SentEmail:
    to: str
    subject: str
    body: str


@dataclass(frozen=True)
class SentSms:
    phone: str
    text: str


@dataclass
class RecordingEmailSender:
    """Substitui o `EmailSender` nos testes e guarda o que foi enviado."""

    sent: list[SentEmail] = field(default_factory=list)

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append(SentEmail(to, subject, body))


@dataclass
class RecordingSmsSender:
    """Substitui o `SmsSender` nos testes e guarda o que foi enviado."""

    sent: list[SentSms] = field(default_factory=list)

    def send(self, phone: str, text: str) -> None:
        self.sent.append(SentSms(phone, text))
