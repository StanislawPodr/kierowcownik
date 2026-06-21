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

Frontend (egzamin testowy) w folderze `static/` (Vue 3):

```bash
cd static
npm install
npm run dev          # dev: http://localhost:5173 (proxy do API)
npm run build        # produkcja: pliki w static/dist/
```

Po `npm run build` otwórz `http://127.0.0.1:8000/` (Django serwuje `static/dist/`).


Endpointy
POST    `/api/auth/register/`
POST    `/api/auth/login/`
POST    `/api/auth/refresh/`
GET     `/api/auth/me/`

(wymagają nagłówka Authorization: Bearer <access>)
GET     '/api/questions/exam/word/'
GET     '/api/questions/exam/category/<symbol>/'
GET     '/api/questions/categories/'

Szczegóły JSON: docs/api-contract.md

## Dane
Link do strony z danymi: https://www.gov.pl/web/infrastruktura/prawo-jazdy 

Załadowanie danych do bazy (plik z pytaniami oraz pliki z video):
```bash
python manage.py parse_questions "plik.xlsx"   
python manage.py add_resources "plik.zip" "plik.zip" ...
```

Dodając flagę --reset usuwane są stare dane przed dodaniem nowych.
