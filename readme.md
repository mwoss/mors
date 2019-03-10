# MORS

Application of topic models for information retrieval and search engine optimization.

### How to run server, step-by-step
```angular2html
> python manage.py makemigrations mors_home
> python manage.py makemigrations mors_seo
> python manage.py migrate
> python manage.py createsuperuser
> python manage.py runserver
```

Server starts at localhost:8000


#### Note:
Before starting server you have to provide pretrained doc2vec, tf-idf and lda models.
Check resources/ directory.