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

Folder fixtures w apce account na repo zawiera dane, którymi można wypełnić db np po jej resecie. Dostępnych jest 4 użytkowników: 2 konta typu standard, jedno staff (czyli admin) i jedno employer. Schemat logowania na przykładzie:

{
   "username": "standard2",
   "password": "standard2"
}

lub

{
   "username": "staff1",
   "password": "staff1"
}

Aby to zrobić, należy użyć polecenia: *python manage.py loaddata test_accounts.json*

Polecenie *loaddata /nazwa_pliku_json/* powoduje przeszukanie folderów fixtures w każdej z apek i wczytanie danych z pliku o podanej nazwie. Aby wczytać wszystkie pliki, wystarczy użyć operatora \*: \*.json
