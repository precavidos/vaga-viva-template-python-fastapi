# Missão `input-validation`: validação e mensagens de erro

Recuse dados inválidos com mensagens claras, no formato padrão da API.

Testes: `tests/missions/test_input_validation.py`. Para rodar só esta missão: `uv run pytest --mission input-validation`.

## Regras para `POST /patients` e `PUT /patients/{id}`

| Campo | Regra |
| --- | --- |
| `name` | obrigatório, não pode ficar em branco |
| `email` | obrigatório, e-mail válido |
| `phone` | obrigatório, não pode ficar em branco |
| `birthDate` | obrigatório, data no passado |

## Formato do erro

Dados inválidos e JSON malformado respondem `400 Bad Request` no formato Problem Details (RFC 9457), com `Content-Type: application/problem+json`:

```json
{
  "type": "about:blank",
  "title": "Bad Request",
  "status": 400,
  "detail": "Dados inválidos. Corrija os campos indicados.",
  "instance": "/patients",
  "errors": [
    {"field": "email", "message": "informe um e-mail válido"},
    {"field": "birthDate", "message": "a data de nascimento precisa estar no passado"}
  ]
}
```

- `status`, `title` e `detail` são obrigatórios. `detail` e as mensagens ficam em **português**.
- Para dados inválidos, `errors` traz um item `{field, message}` para **cada** campo inválido, todos de uma vez. `field` é o nome do campo no JSON.
- Para JSON malformado, `errors` é opcional.

Por padrão, o FastAPI responde `422` com mensagens em inglês. Os tratadores de erro ficam em `configure_error_handlers` (`app/errors.py`), que `create_app()` já chama: os testes sobem a aplicação por ela.
