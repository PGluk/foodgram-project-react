# Дипломная работа Foodgram

## Описание

Проект Foodgram - сервис для публикации кулинарных рецептов. 

Демоверсия сайта: <http://foodgram.myddns.me>

Админ панель: <http://foodgram.myddns.me/admin/>

Тестовый пользователь: 
- login: test@test.ru
- password: test

Возможности сервиса:

- Регистрация пользователей.
- Создание, Изменение, Удаление рецептов.
- Добавление рецептов в избранное и простмотр всех избранных рецептов.
- Фильтрация рецептов по тегам.
- Подписка на авторов и просмотр рецептов определенного автора.
- Добавление рецептов и формирование списка покупок для их приготовления.

- ###Установка
Для работы с проектом необходимо установить Docker: <https://docs.docker.com/engine/install/>


 - Клонируйте репозиторий к себе на сервер командой:
```bash
https://github.com/PGluk/foodgram-project-react
```

Перейдите в каталок проекта:
```bash
cd foodgram-project-react
```
Создайте файл окружений
```bash
touch .env
```
И заполните его:
```bash
POSTGRES_NAME=postgres  # имя базы postgres
POSTGRES_USER=postgres # имя пользователя postgres
POSTGRES_PASSWORD=postgres # пароль для базы postgres
DB_HOST=postgresql   #имя хоста базы данных
DB_PORT=5432  #порт
```


Перейдите в каталог infra и запустите создание контейнеров:
```bash
docker-compose up -d --build
```

Первоначальная настройка проекта:
```bash
- docker-compose exec backend python manage.py migrate --noinput
- docker-compose exec backend python manage.py collectstatic --no-input
```
Создание суперпользователя:
```bash
- docker-compose exec backend python manage.py createsuperuser
```
Загрузка фикстур
```bash
docker exec -it backend python manage.py loaddata fixtures.json
```
После сборки, проект будет доступен по имени хоста вашей машины, на которой был развернут проект. 

Проект подготовил Глухов Павел, в рамках учебной программы по бекенд разработке ЯПрактикум.
