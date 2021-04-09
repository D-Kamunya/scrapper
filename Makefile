install:
	pip install -r requirements.txt

migrations:
	python manage.py makemigrations

migrate:
	python3 manage.py migrate

jobscrap:
	@[ "${platform}" ] || ( echo ">> Platform to initialize scrapping not set"; exit 1 )
	if [ $(platform) = freelancermap ]; then \
        python3 manage.py jobscrap -p $(platform) -e $(email) -pwd $(pass) -l $(location) -t $(title); \
    else \
				python3 manage.py jobscrap -p $(platform) -l $(location) -t $(title); \
		fi

movie:
	python3 manage.py moviedownloader -s $(site) -t $(title) -se $(season) -ep $(episode)

celery:
	celery -A scrapper  worker -B -l info

superuser:
	python manage.py createsuperuser

collectstatic:
	python manage.py collectstatic

serve:
	python3 manage.py runserver

shell:
	python manage.py shell

set_env_vars:
	source venv/bin/activate;

.PHONY: set_env_vars
				movie clean
