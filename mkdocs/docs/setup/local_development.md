# Setting up a local copy of Cores for development

!!! info
    A quick PSA, the actual Django application for Cores is located in `[git root]/cores`, the other directories contain
    supporting bits for the Docker stack. You'll want to be working here for most things.

## Prerequisites

We're going to assume you've got a Debian bash terminal to hand, either using [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/about)
or running natively. To setup WSL, take a look [here](https://docs.microsoft.com/en-us/windows/wsl/install-win10). It probably
could run on Windows, but that hasn't been tested.

### Python tools

This project relies on Python 3, so grab yourself a copy of that and `pip3`. We also need a couple of extra development
bits to build up the LDAP and Kerberos plugins for Django. It's also worth working in a `pip` virtualenv to keep our system
Python tidy.

```bash
sudo apt-get update

# python,  pip, and ldap/kerberos dev bindings
sudo apt-get install -y python3 python3-pip libldap2-dev libkrb5-dev

# pip virtualenv
pip3 install virtualenv
```

### Database

We also need a [PostgreSQL](https://www.postgresql.org/) database, we can't use the default development SQlite as we rely
on some rather trick fields and lookup types for `django-netfields`.

You've got two options:

 1. Run Postgres locally on your machine
 2. Spin up a Postgres container in Docker (easier if you've got Docker set up)

If you're going the Docker route, it's a one-liner:

```sh
$ docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -d cores
```

> This creates a Postgres instance on localhost with database name 'cores' and superuser 'postgres' with password 
> 'mysecretpassword'.

Otherwise, we've got some more work to do:

 1. Grab Postgres if you haven't already:
    `apt-get install postgresql-10`
 2. Start up the pgsql daemon:
    `systemctl start pgsql`
 3. Create the database and user:
    - `su` to the database user: `sudo su postgres`
    - Create the user: `createuser --interactive --pwprompt`
      > Enter name of role to add: _cores_ <br/>
      > Enter password for new role: _cores_ <br/>
      > Enter it again: <br/>
      > Shall the new role be a superuser? (y/n) _y_
    - Create the database: `created -O cores cores`
      > database name 'cores' with owner 'cores'

That should be the database all set up.

## The virtualenv

!!! info "Reminder"
    We're working in `[root]/cores/`, **not** in the project root.

To keep things tidy, we can work in a virtualenv, it's not entirely necessary though. To create your virtualenv and activate
it, run the following:

```bash
virtualenv cores-venv
source ./cores-venv/bin/activate
```

Keep an eye on the output, it should create the virtualenv using Python3. You'll have `(cores-venv)` prepended to your
terminal prompt when the virtualenv is active.

Now we can install all the `pip` packages used by Cores:

```
pip install -r ./requirements.txt
```

Assuming that all installs fine, you're good to go.

## The config envfile

All of the config is pulled in through environment variables, so you'll also need to copy and fill in `envfile.template.sh`,
before running `source` on it to populate your shell.

```bash
#!/bin/bash

# source me before trying to start Cores if you're running
# locally rather than in Docker. It gets very upset if you
# don't have some of these set.

export HOSTNAME=cores # Django will only accept requests from defined hostnames (localhost always included)
export SECRET_KEY=uhaegagoihierghaoeguiaeguiagr
export DEBUG=True

# database
export POSTGRES_HOST=localhost
export POSTGRES_PASSWORD=password
export POSTGRES_USER=django

# LDAP or Kerberos config
export LDAP_AUTH=False # enable LDAP
export LDAP_AUTH_DIRECT=False # enable direct bind LDAP (only if normal LDAP not enabled)
export LDAP_URI=ldap://dc01.contoso.com # where to bind to
export LDAP_BIND_DN=bind-user # creds for queries
export LDAP_BIND_PASS=password
export LDAP_SEARCH_PATH=OU=Users,OU=All Sites,DC=Contoso,DC=Com # where to search for users
export LDAP_LOGGING=False # extra debug logs
export KERBEROS_AUTH=False # enable (experimental) Kerberos authentication
export KERBEROS_REALM=contoso.com
export KERBEROS_SERVICE=dc02.contoso.com/FINANCE

# leave SMTP server blank if not in use
export SMTP_SERVER=False # set server here if you want emails
export SMTP_PORT=25
export SMTP_FROM=noreply@cores.local
```

## Start it up

You're now ready to start up Cores.

* `python3 manage.py makemigrations booking inventory notices live api loans` - Prepare DB migration scripts (should
already have been done by last developer)
* `python3 manage.py migrate` - Run migrations and prepare database.
* `python3 manage.py runserver` - Start up a development server on `localhost:8000`.

## Setup superuser (BONUS)

Now the database is populated, we can create the initial superuser from the command line:

```
python3 manage.py createsuperuser
```

You will be asked for a username, email address and password. It's probably worth picking something
different to your LDAP username if you're going to be testing that out as well, as Django automatically
maps LDAP usernames to Django usernames.

## What next?

!!! success
    Congrats, you've now got a copy of Cores running on your machine. The Django development server
    also supports auto-reload when you change any source which is handy.

Here's some other stuff to look at:

  - Database looking a bit sparse? Take a look at the [LabLiveScan importer](../../import_scripts/lablivescan/).
  - Want to know more about how the project is structured? The [developer guide](../../developer_guide/) might help.
  - How about a production setup with WSGI? We can do [that](../production_docker_deployment/) with Docker.
