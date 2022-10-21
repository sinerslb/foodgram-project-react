# Foodgram

Приложение для обюмена рецептами блюд. Позволяет посматривать рецепты других пользователей, подписываться на пользователей, Вести список любимых рецептов и формировать список необходимых покупок, для приготовления выбранных рецептов.

![Foodgram workflow](https://github.com/sinerslb/foodgram-project-react/actions/workflows/yamdb_workflow.yml/badge.svg)

### Развёртывание
1. Создать репозиторий с проектом  
2. Добавить в Secrets GitHub Actions репозитория переменные окружения  
    - для работы Django:
      ```
      SECRET_KEY - секретный ключ Django
      ```
    - для работы базы данных:
      ```
      DB_ENGINE - движок базы данных (укажите django.db.backends.postgresql)
      DB_NAME - имя базы данных
      POSTGRES_USER - логин для подключения к базе данных
      POSTGRES_PASSWORD - пароль для подключения к базе данных
      DB_HOST= - название сервиса (контейнера)
      DB_PORT=5432 - порт для подключения к базе данных
      ```
    - для подключения к Docker hub:
      ```
      DOCKER_USERNAME - имя пользователя Docker
      DOCKER_PASSWORD - пароль пользователя Docker
      ```
    - для подключения к удаленному серверу:
      ```
      HOST - ip адрес удалённого сервера
      USER - имя пользователя удалеённого сервера
      SSH_KEY - закрытая часть ключа SSH
      PASSPHRASE - пароль
      ```
    - для информирования в Telegram через telegram-бота:
      ```
      TELEGRAM_TO - id чата для информирования
      TELEGRAM_TOKEN - id информирующего бота
      ```
3. Скопируйте файлы infra/docker-compose.yaml и infra/nginx/default.conf из вашего проекта на сервер в  
home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx/default.conf соответственно.
4. При первом развёртывании подключиться к удалённому серверу, и выполнить команды:
    ```
    sudo docker-compose exec web python manage.py migrate --noinput
    sudo docker-compose exec web python manage.py collectstatic --no-input
    sudo docker-compose exec web python manage.py createsuperuser
    ```
5. Проект развёрнут по адресу [siteforpractikum.sytes.net](http://siteforpractikum.sytes.net) или по ip адресу [51.250.110.174](http://51.250.110.174).

### Стек технологий
- Python 3.7
- Django 2.2.19
- Django REST framework 3.12.4
- Nginx
- Docker
- Postgres

### Автор
Алексей Андреев