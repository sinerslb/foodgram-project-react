# Foodgram

Приложение для обюмена рецептами блюд. Позволяет посматривать рецепты других пользователей, подписываться на пользователей, вести список любимых рецептов и формировать список необходимых покупок, для приготовления выбранных рецептов.

![Foodgram workflow](https://github.com/sinerslb/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

### Развёртывание
1. Создать репозиторий с проектом  
2. Добавить в Secrets GitHub Actions репозитория переменные окружения  
    - для работы Django:
      ```
      SECRET_KEY - секретный ключ Django
      DEBUG - True для рехима отладки или False
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

3. Скопируйте файлы infra/docker-compose.yaml и infra/nginx.conf из вашего проекта на сервер в home/<ваш_username>/
4. При первом развёртывании подключиться к удалённому серверу и выполнить команды:
    ```
    sudo docker-compose exec backend python manage.py migrate --noinput
    sudo docker-compose exec backend python manage.py collectstatic --no-input
    sudo docker-compose exec backend python manage.py createsuperuser
    ```
5. Проект развёрнут по адресу [siteforpractikum.sytes.net](http://siteforpractikum.sytes.net) или по ip адресу [51.250.110.174](http://51.250.110.174). Учётная запись администратора admin@foodgram.fake, пароль admin.


### Стек технологий
- Python 3.7
- Django 2.2.19
- Django REST framework 3.12.4
- Nginx
- Docker
- Postgres

### Автор
Алексей Андреев