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

### GET/POST `/api/questions/progress/`

Synchronizacja postępu nauki (błędne / oznaczone / obejrzane pytania).

GET odpowiedź `200`:

```json
{
  "wrong_questions": [1, 5],
  "marked_questions": [3],
  "seen_questions": [1, 2, 3, 5]
}
```

POST (wszystkie pola opcjonalne):

```json
{
  "wrong_questions": [1, 5],
  "marked_questions": [3],
  "seen_questions": [1, 2, 3, 5]
}
```

### POST `/api/questions/exam-attempts/`

Zapis podsumowania ukończonego egzaminu.

```json
{
  "category": "B",
  "score": 70,
  "max_score": 74,
  "passed": true
}
```

Odpowiedź `201`:

```json
{
  "id": 1,
  "category": "B",
  "score": 70,
  "max_score": 74,
  "passed": true,
  "percent": 95,
  "created_at": "2026-06-20T12:00:00Z"
}
```

### GET `/api/questions/exam-attempts/`

Historia egzaminów zalogowanego użytkownika. Opcjonalny filtr: `?category=XXX`.
Odpowiedź `200`, tablica obiektów jak wyżej.

### GET `/api/questions/exam-attempts/stats/`

Odpowiedź `200`:

```json
{
  "total_attempts": 5,
  "passed_count": 3,
  "pass_rate": 60,
  "avg_score": 65.2,
  "last_attempt": {
    "id": 5,
    "category": "B",
    "score": 70,
    "max_score": 74,
    "passed": true,
    "percent": 95,
    "created_at": "2026-06-20T12:00:00Z"
  }
}
```