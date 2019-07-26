docker-compose stack
===

This project does use a few components, and they can make a bit of a mess to your system as they
set themselves up. (go Python, I guess?) To keep things portable, it's all been structured to live
inside [Docker](https://www.docker.com/) containers, a very lightweight and dare I say it, trendy, 
containerisation platform.

Components
---

The base setup includes the following containers:

|    Name    | Role | Base image |
|------------|------|------------|
| **cores**  | the core Django application, running as a WSGI endpoint. [More info](../developer_guide). | [Python:3.7](https://hub.docker.com/_/python) |
| **mkdocs** | builds these docs and dumps them into a volume for nginx to use | [squidfunk/mkdocs-material](https://hub.docker.com/r/squidfunk/mkdocs-material) |
| **nginx**  | WSGI server, also serves static assets and docs from volumes | [nginx:alpine](https://hub.docker.com/_/nginx)|
| **postgres** | database | [postgres:latest](https://hub.docker.com/_/postgres) |

Volumes
---

In the Docker world, you can mount persistent storage into the containers through [volumes](https://docs.docker.com/storage/volumes/). In this case, we have
three volumes set up, two internal (not accessible by host) and one mounting a host directory through. 

| Name | Role | Mounted to | Mount point |
|------|------|------------|-------------|
| `static_volume` | Sharing static assets collected by `python manage.py collectstatic` across to the nginx webserver that will be hosting them | cores, nginx | internal |
| `postgres_data` | Persistent data volume for database | postgres | internal |
| `mkdocs_site` | Sharing built documentation site to nginx | mkdocs, nginx | internal |

!!! warning
    Because of these volumes, it is safe to destroy and recreate the containers (say, for an update) as all data 
    is persisted outside of them. Saying that, it is fairly easy to delete the volumes if you're not careful. **If
    the volumes are destoyed, so is all the app's data.**

Build scripts
---

There are two tiers of scripts in this project, the container level [Dockerfiles](https://docs.docker.com/engine/reference/builder/)
and the project level [Docker compose file](https://docs.docker.com/compose/overview/)

Dockerfiles handle the build and configuration of the containers, the compose file builds the stack, sets up
networking and volumes, and configures the host to map out the necessary ports.

In most cases you shouldn't need to touch the Dockerfiles, all config can be accessed from the compose file.

### Project Docker-compose

This is provided as a template in `docker-compose.template.yml` and will require some editing before it's ready 
to go. The containers have been set to grab their config from environment variables, and the compose file is all
set up to pass these through. Just copy this to a new file called `docker-compose.yml` and fill in the blanks.

!!! danger
    Heads up, a completed docker-compose contains secrets and other private info. It's in the `.gitignore` for
    these reasons, and shouldn't be pushed to the repository. It's probably also worth setting the permissions
    as follows:
    ```bash
    sudo chown root:docker ./docker-compose.yml
    sudo chmod 660 ./docker-compose.yml
    ```

```yaml
version: '3.2'

volumes:            # define persistent volumes
  static_volume:
  postgres_data:
  mkdocs_site:

services:

  cores:            # django app
    build:
      context: ./cores
    links:
      - postgres:postgres
    environment:
      # basic setup
      - HOSTNAME=cores # which hostname should django accept requests from (in addition to localhost)
      - SECRET_KEY=uhriagseruiguaeiorghozagraioehgr # make some entropy
      - DEBUG=False # turn on the *very* (dangerously) verbose error pages

      # database
      - POSTGRES_HOST=postgres # hostname of psql in docker stack
      - POSTGRES_PASSWORD=password # pick a password
      - POSTGRES_USER=django
      
      # authentication (LDAP or Kerberos)
      - LDAP_AUTH=False # enable LDAP
      - LDAP_AUTH_DIRECT=False # enable direct bind LDAP (only if normal LDAP not enabled)
      - LDAP_URI=ldap://dc01.contoso.com # where to bind to
      - LDAP_BIND_DN=bind-user # creds for queries
      - LDAP_BIND_PASS=password
      - LDAP_SEARCH_PATH=OU=Users,OU=All Sites,DC=Contoso,DC=Com # where to search for users
      - LDAP_LOGGING=False # extra debug logs

      - KERBEROS_AUTH=False # enable (experimental) Kerberos authentication
      - KERBEROS_REALM=contoso.com
      - KERBEROS_SERVICE=dc02.contoso.com/FINANCE

      # mail
      - SMTP_SERVER=False # set server here if you want emails
      - SMTP_PORT=25
      - SMTP_FROM=noreply@cores.local
    depends_on:
      - postgres
    restart: always
    volumes:
      - static_volume:/srv/static
  
  postgres:
    image: postgres
    restart: always
    environment:
      - POSTGRES_DB=cores
      - POSTGRES_USER=django
      - POSTGRES_PASSWORD=[password] # set to the same as defined above
    command: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    # no config necessary
  
  docs:
    # no config necessary
```

### Container Dockerfiles

These are very simple, taking the `cores` Dockerfile as an example:

```dockerfile
# pull down the base image from the Docker hub
FROM python:3.7

# let the docker daemon know this has a service on port 8000 and that 
# we're expecting a volume
EXPOSE 8000
VOLUME ["/srv/static"]

# cd into our app directory, add some files, run some commands
WORKDIR /srv/cores
ADD requirements.txt /srv/cores
RUN pip install -r requirements.txt
ADD . /srv/cores

# define what runs when the container is started
ENTRYPOINT ["bash", "/srv/cores/start.sh"]
```

There's plenty more info on what you can do in these files on the [Docker docs](https://docs.docker.com/engine/reference/builder/).

!!! tip
    These are **run when the stack is first started**, and thereafter you'll need to explicitly ask compose
    to rebuild them with the `--build` flag. Otherwise they are stored as an image. **Each step is also cached**,
    so if you're changing something a lot, stick it towards the end of the Dockerfile and it will only rebuild
    the steps following what you've changed.

Internal networking
---

The compose script only exposes containers to the host/wider world if the port has been tagged in the compose file.
In the case of this project, the only thing that can be accessed externally is port 80 on the `nginx` container.

Saying that, the containers are all networked together in a private network created automatically by the compose 
script. This means each container can access the other containers by referring to them by their service name, as 
defined in the compose file - in our case `cores`, `docs`, `postgres` and `nginx`. The compose script sets host
file entries for each of the containers so they can be accessed by hostname.

### SSH access to containers

Because of this networking segregation, you can't SSH into the containers in a traditional sense. You have to go
via the Docker daemon. Thankfully this is very easy, you can run `docker-compose exec [container] bash` to open
up an interactive bash session on the container.

!!! note
    **You can only open an SSH session to a running container.** Docker will automatically stop a container if
    the application process inside dies, if this is the case you'll either have to start a new instance of the
    container with `docker run -it [image name] bash` or change the compose file start attribute/Dockerfile 
    entrypoint to something long-running so you get a chance to connect in. Also, *the Alpine containers
    don't have bash* so you will have to use `sh` instead.
