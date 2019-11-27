# Usamo_backend

## Docker compose run
Dodane są 2 serwisy: 
 - db - baza danych
 - web - podstawowa strona

Do uruchomienia potrzebny jest zainstalowany docker i docker-compose

Uruchamiamy poleceniem 'docker-compose up' w głównym katalogu (tam gdzie plik docker-compose.yml
Jeśli jest to pierwsze uruchomienie aplikacji trzeba przed tym puścić migracje komendą 'docker-compose run web python manage.py migrate

Aby sprawdzić działanie np. w przeglądarce należy zmienić 'localhost' na adres ip wirtualnej maszyny. Ip maszyny można sprawdzić komendą 'docker-machine ip'

Wyłączanie: Ctrl+c lub bardziej elegancko w drugiej konsoli docker-compose down
