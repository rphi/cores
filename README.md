# Cores

### a proof of concept for a new lab management database

This project is built with Django 2.2 on Python3. You'll probably want a Virtualenv, but just
`pip install -r requirements.txt` to get set up, and `python manage.py runserver` to get a development
server spun up on localhost. **NOTE**: the django-netfields powered database fields don't work in 
SQlite, used by the default Django development server. To test these features you'll need Postgres.

You can also deploy with Docker Compose, simply tweak the env vars in the `docker-compose.template.yml `
to match your environment, then run `docker-compose up -d` to spin up the nginx, postgres,
build the docs with MkDocs and start the Django app in WSGI mode.

## Components

In Django terminology, the project name is `cores` and each component is registered as its own `app` with
independent URL routing and template storage. Shared config, static files and templates are located in the
`cores` directory.

- **booking**: server and VM booking
- **inventory**: server asset management
- **live**: ingests live scan data (ip/mac mappings) and flags conflicts with the database
- **reports**: basic reports generation from the db
- **notices**: allows messages to be posted onto the booking dashboard

Each app has its own section in the Django admin.

## Docs
So the docs are currently designed to work with [MkDocs](https://www.mkdocs.org/) however you can view
them just fine as they're Markdown. They're in the [/mkdocs](mkdocs/docs) folder, and are generated and
stuck on /docs when the Docker compose stack is built.
