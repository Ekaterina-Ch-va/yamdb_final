# yamdb_final
![example workflow](https://github.com/Ekaterina-Ch-va/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
![example branch parameter](https://github.com/Ekaterina-Ch-va/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?branch=feature-1)
![example event parameter](https://github.com/Ekaterina-Ch-va/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?event=push)
## Описание:
> Концепция проекта YaMDb:
>> Проект YaMDb собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка». Например, в категории «Книги» могут быть произведения «Винни-Пух и все-все-все» и «Марсианские хроники», а в категории «Музыка» — песня «Давеча» группы «Жуки» и вторая сюита Баха. Список категорий может быть расширен (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»). 
Произведению может быть присвоен жанр из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»). 
Добавлять произведения, категории и жанры может только администратор.
Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — рейтинг (целое число). На одно произведение пользователь может оставить только один отзыв.
Пользователи могут оставлять комментарии к отзывам.
Добавлять отзывы, комментарии и ставить оценки могут только аутентифицированные пользователи.

> Для реализации использовались Django REST Framework, Docker, Nginx,
СУБД PostgreSQL, WSGI-сервер Gunicorn.
> Проект доступен здесь:(http://84.201.129.162/redoc/) 


### Шаблон наполнения env-файла.
> Откройте любым доступным редкатором файл .env и укажите в нем следующую информацию:

1. Указываем БД проекта:
DB_ENGINE='DB_ENGINE'

2. Имя базы данных:
DB_NAME='DB_NAME'

3. Логин для подключения к базе данных:
POSTGRES_USER='USER'

4. Пароль для подключения к БД:
POSTGRES_PASSWORD='PASSWORD'

5. Название сервиса (контейнера):
DB_HOST='localhost'

6. Порт для подключения к БД:
DB_PORT='5432'

7. Секретный ключ из файла settings проекта:
SECRET_KEY='SECRET KEY'


### Описание команд для запуска приложения в контейнерах:
1. Запуск сборки контейнеров:
docker-compose up -d

2. Подготовка к выполнению миграций: 
docker-compose exec web python manage.py makemigrations 

3. Запуск миграций:
docker-compose exec web python manage.py migrate

4. Создание суперпользователя:
docker-compose exec web python manage.py createsuperuser

5. Сбор статики в одном месте ('/static/'):
docker-compose exec web python manage.py collectstatic --no-input 

> Проверьте работоспособность приложения


### Описание команды для заполнения базы данными:
1. Копируйте файл fixtures.json с локального компьютера на сервер.
Из консоли выполните комманду:
scp my_file username@host:<путь-на-сервере(до папки с файлом manage.py)>

2. Выполните из терминала на сервере слудующие команды для переноса данных:
python3 manage.py shell  
>>> from django.contrib.contenttypes.models import ContentType
>>> ContentType.objects.all().delete()
>>> quit()
python manage.py loaddata fixtures.json


