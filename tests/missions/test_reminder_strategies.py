from datetime import date

import pytest

from app.reminders.dependencies import get_reminder_strategies
from app.reminders.reminder import ReminderChannel
from tests.support.api import Api, expect_status
from tests.support.database import Database
from tests.support.dates import MONDAY, at, future_date
from tests.support.patients import create_patient, new_patient
from tests.support.recording_senders import RecordingEmailSender, RecordingSmsSender

pytestmark = pytest.mark.mission("reminder-strategies")

PROFESSIONAL_NAME = "Dr. Rafael Moura"
MONDAY_DATE = future_date(MONDAY)
EXPECTED_PARTS = (PROFESSIONAL_NAME, date.fromisoformat(MONDAY_DATE).strftime("%d/%m/%Y"), "10:15")


def schedule_appointment(api: Api, db: Database, patient: dict[str, str]) -> int:
    patient_id = create_patient(api, patient)
    professional_id = db.insert_professional(PROFESSIONAL_NAME, "Cardiologia")
    return db.insert_appointment(professional_id, patient_id, at(MONDAY_DATE, "10:15"), 30)


def test_envia_o_lembrete_por_email_para_o_email_do_paciente(api, db, emails, sms):
    patient = new_patient()
    appointment_id = schedule_appointment(api, db, patient)

    response = api.post(f"/appointments/{appointment_id}/reminders?channel=EMAIL")

    expect_status(response, 202, "esperava status 202 em POST /appointments/{id}/reminders?channel=EMAIL")
    assert len(emails.sent) == 1, "esperava exatamente um e-mail enviado pelo EmailSender"
    email = emails.sent[0]
    assert email.to == patient["email"], "esperava o e-mail enviado para o endereço do paciente"
    assert email.subject.strip(), "esperava um assunto no e-mail"
    for part in EXPECTED_PARTS:
        assert part in email.body, (
            "esperava no texto do e-mail o profissional, a data (dd/MM/aaaa) e a hora (HH:mm): "
            f"'{part}'; recebeu {email.body!r}"
        )
    assert sms.sent == [], "esperava que o lembrete por e-mail não enviasse SMS"


def test_envia_o_lembrete_por_sms_para_o_telefone_do_paciente(api, db, emails, sms):
    patient = new_patient()
    appointment_id = schedule_appointment(api, db, patient)

    response = api.post(f"/appointments/{appointment_id}/reminders?channel=SMS")

    expect_status(response, 202, "esperava status 202 em POST /appointments/{id}/reminders?channel=SMS")
    assert len(sms.sent) == 1, "esperava exatamente um SMS enviado pelo SmsSender"
    message = sms.sent[0]
    assert message.phone == patient["phone"], "esperava o SMS enviado para o telefone do paciente"
    for part in EXPECTED_PARTS:
        assert part in message.text, (
            f"esperava no SMS o profissional, a data (dd/MM/aaaa) e a hora (HH:mm): '{part}'; recebeu {message.text!r}"
        )
    assert emails.sent == [], "esperava que o lembrete por SMS não enviasse e-mail"


def test_tem_uma_estrategia_reminder_strategy_para_cada_canal():
    strategies = get_reminder_strategies(RecordingEmailSender(), RecordingSmsSender())

    assert sorted(strategy.channel for strategy in strategies) == sorted(ReminderChannel), (
        "esperava em get_reminder_strategies uma ReminderStrategy para cada canal (EMAIL e SMS)"
    )
    assert len({type(strategy) for strategy in strategies}) == len(strategies), (
        "esperava uma classe diferente para cada canal"
    )
