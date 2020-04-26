# Usamo_backend

## Docker compose run
Dodane są 2 serwisy: 
 - db - baza danych
 - web - podstawowa strona

Do uruchomienia potrzebny jest zainstalowany docker i docker-compose

Uruchamiamy poleceniem 'docker-compose up --build' w głównym katalogu (tam gdzie plik docker-compose.yml). Flaga '--build' powoduje zbudowanie serwisów, więc jest wymagana przy pierwszym uruchomieniu, później w zależności od preferencji.
Jeśli jest to pierwsze uruchomienie aplikacji trzeba przed tym puścić migracje komendą 'docker-compose run web python manage.py migrate

Aby sprawdzić działanie np. w przeglądarce należy zmienić 'localhost' na adres ip wirtualnej maszyny. Ip maszyny można sprawdzić komendą 'docker-machine ip'

Wyłączanie: Ctrl+c lub bardziej elegancko w drugiej konsoli docker-compose down

## Defaultowe dane w bazie

Foldery fixtures w apkach na repo zawierają dane, którymi można wypełnić db np po jej resecie: 
 - Account: dostępnych jest 19 użytkowników: 8 kont typu standard, 6 staff (kolejno dla każdej grupy uprawnień: weryfikacja użytkowników, zarządzanie cv, zarządzanie ofertami pracy, blog - creator, blog - moderator + jedno konto, które ma wszystkie te uprawnienia) i 5 employer. Schemat logowania na przykładzie:

{
   "username": "standard2",
   "password": "standard2"
}

lub

{
   "username": "staff1",
   "password": "staff1"
}

Wyjątek -- konto admina ze wszystkimi uprawnieniami

{
   "username": "staff_super",
   "password": "staff_super"
}

-CV: stworzyłem jedno cv z feedbackiem (bez zdjęcia) dla użytkownika standard1 i 2 bez feedbacku dla standard 2. Nie ma sensu odpalać urli do nich, bo pdf'ów fizycznie nie będzie na serwerze - zresztą heroku i tak co reset usuwa pliki statyczne. Można je natomiast wykorzystać do testowania endpointów do kasowania, czytania danych cv, listy cv itd. 

-Job: dwie oferty pracy stworzone przez użytkownika employer1 i jedna przez employera2. Pierwsza z nich ma 1 aplikacje od standard1, druga ma dwie aplikacje od standard1 i standard2.

-Blog: dwa posty od użytkownika staff4, jeden z nich ma dwa komentarze.

Aby załadować dane do bazy, należy użyć polecenia: *python manage.py loaddata nazwa.json* (info dla backendu)

## Zmienne środowiskowe i settings

Przeniesony został plik settings.py z katalogu głównego modułu usamo do podkatalogu "settings". Wiąże się to ze zmianą zmiennej środowiskowej tak jak to zostało opisane poniżej. W przypadku braku tej zmiennej ustawiana jest domyślna wartość "usamo.settings.settings"

Główne envy do ustawienia:

- SECRET_KEY: sekret aplikacji
- DJANGO_SETTINGS_MODULE: domyślny powinien być "usamo.settings.settings", jeśli macie lokalnie ustawioną zmienną środowiskową na inną wartość, aplikacja się nie uruchomi

Dodatkowe, obecnie tylko dla ustawień "test" i "prod" - czyli dla dockera i heroku:
- POSTGRES_DB: nazwa bazy
- POSTGRES_USER: nazwa użytkownika postgresa
- POSTGRES_PASSWORD: hasło użytkownika postgresa
dla dev używamy domyślnych ustawnień bazy, takich jakie są podane w usamo.settings.settings.py
