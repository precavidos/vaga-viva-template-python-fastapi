# Missão `reminder-strategies`: lembretes por e-mail e SMS

Envie lembretes de consulta por canais diferentes, aplicando um padrão de projeto com dependências do FastAPI.

Testes: `tests/missions/test_reminder_strategies.py`. Para rodar só esta missão: `uv run pytest --mission reminder-strategies`.

## O que o código inicial já traz

Pasta `app/reminders`:

- `EmailSender` e `SmsSender` (`senders.py`), fornecidos pelas dependências `get_email_sender` e `get_sms_sender` (`dependencies.py`): quem de fato envia. As implementações do código inicial só escrevem no log; nos testes, elas são trocadas, por `app.dependency_overrides`, por versões que guardam o que foi enviado.
- `ReminderChannel` (`reminder.py`): os canais, `EMAIL` e `SMS`.
- `ReminderStrategy` (`strategy.py`): o contrato de um canal de lembrete.
- `get_reminder_strategies` (`dependencies.py`): a dependência que fornece a lista de estratégias (`list[ReminderStrategy]`), a partir dos dois senders.
- `Reminder` (`reminder.py`): os dados de um lembrete.
- `router.py`: o `APIRouter` dos lembretes, já registrado em `create_app()`.

## Contrato

- Cada canal tem a sua implementação de `ReminderStrategy`, uma classe por canal. A lista devolvida por `get_reminder_strategies` traz uma estratégia para cada canal.
- `POST /appointments/{id}/reminders?channel=EMAIL` ou `?channel=SMS` envia o lembrete da consulta `{id}` pelo canal pedido e responde `202 Accepted`. A rota recebe as estratégias por `Depends(get_reminder_strategies)`, para que os testes possam trocar os senders.
- E-mail: enviado por `EmailSender` para o e-mail do paciente, com assunto.
- SMS: enviado por `SmsSender` para o telefone do paciente.
- O texto traz o nome do profissional, a data no formato `dd/MM/aaaa` e a hora no formato `HH:mm`. Exemplo: `Lembrete: consulta com Dr. Rafael Moura em 04/03/2030 às 10:15.`
- Um lembrete por um canal não envia nada pelo outro.
