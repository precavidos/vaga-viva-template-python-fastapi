# Missão `bug-hunt`: caça ao bug

Encontre e corrija um defeito escondido no cálculo da duração das consultas.

Testes: `tests/missions/test_bug_hunt.py`. Para rodar só esta missão: `uv run pytest --mission bug-hunt`.

## Contrato

- O cálculo fica em `appointment_duration(start, end)`, em `app/appointments/duration.py`, que devolve a duração em minutos (`int`) entre dois `datetime`.
- O resultado precisa estar certo para qualquer par de datas em que `end` vem depois de `start`, inclusive em dias diferentes.
- Mantenha a assinatura da função: outras partes do sistema a usam.
- Os testes da missão mostram os casos em que o resultado sai errado. Antes de corrigir, entenda por quê.
