Bazowy URL (dev): `http://127.0.0.1:8000`

## Publiczne endpointy

### POST `/api/auth/register/`

```json
{
  "username": "janek",
  "password": "haslo12345",
  "password_confirm": "haslo12345"
}
```

Odpowiedź `201`:

```json
{
  "id": 1,
  "username": "janek"
}
```

### POST `/api/auth/login/`

```json
{
  "username": "janek",
  "password": "haslo12345"
}
```

Odpowiedź `200`:

```json
{
  "access": "<jwt>",
  "refresh": "<jwt>"
}
```

### POST `/api/auth/refresh/`

```json
{
  "refresh": "<jwt>"
}
```

Odpowiedź `200`:

```json
{
  "access": "<jwt>"
}
```

## Chronione endpointy

Nagłówek: `Authorization: Bearer <access>`

### GET `/api/auth/me/`

Odpowiedź `200`:

```json
{
  "id": 1,
  "username": "janek"
}
```

## Test z PowerShell (curl)

```powershell
curl -X POST http://127.0.0.1:8000/api/auth/register/ -H "Content-Type: application/json" -d "{\"username\":\"janek\",\"password\":\"haslo12345\",\"password_confirm\":\"haslo12345\"}"
```
