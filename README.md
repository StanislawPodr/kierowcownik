# kierowcownik
To build and run use:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd app 
python3 manage.py migrate
python3 manage.py runserver
```


Endpointy
POST    `/api/auth/register/`
POST    `/api/auth/login/`
POST    `/api/auth/refresh/`
GET     `/api/auth/me/`

Szczegóły JSON: docs/api-contract.md

## Testy

```bash
cd app
python3 manage.py test accounts
```