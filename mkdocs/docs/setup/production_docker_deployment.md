---
title: Production (Docker) deployment
---

# Deploying to production with Docker

## Prerequisites

If your machine doesn't have Docker, it's pretty quick to get set up:

* Docker for Windows *(requires Hyper-V, breaks VirtualBox, includes cli and compose for PowerShell)*: [Get from Docker Hub](https://hub.docker.com/editions/community/docker-ce-desktop-windows)
* Docker CE for CentOS: [docs on Docker.com](https://docs.docker.com/install/linux/docker-ce/centos/) 

!!! warning "PSA"
    The `docker-compose` tool isn't installed by default on Linux builds, you'll need to get that seperately - there's
    a guide [here](https://docs.docker.com/compose/install/). You'll also want to add yourself to the `docker` group
    to save you having to `sudo` all the Docker commands.

!!! tip
    It's also worth sticking [Portainer](https://www.portainer.io/) on the host, which gives you a nice web UI to 
    make managing Docker easier, and give you really easy access to things like container consoles and image lists.
    You can get it up and running with this once you've got Docker installed - it's a container itself:

    ```docker run -d -p 9000:9000 -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer --restart always```

    You'll then have the UI up on [localhost:9000](http://localhost:9000).

## Just ship it

If you're starting from a fresh database, you've got a few steps to get everything up and running:

!!! notice "Important"
    Before trying to start any of the stack, make sure you've made a copy of the `docker-compose.template.yml`
    into `docker-compose.yml` and filled in the configuration. For more info on the options, see [here](../../docker-compose/#project-docker-compose).
!!! danger
    A completed docker-compose contains secrets and other private info. It's in the `.gitignore` for
    these reasons, and shouldn't be pushed to the repository. It's probably also worth setting the permissions
    as follows:
    ```bash
    sudo chown root:docker ./docker-compose.yml
    sudo chmod 660 ./docker-compose.yml
    ```

1.  Fill in the `POSTGRES_` and `HOST` details as a minimum on the `cores` container, and copy those onto the corresponding
    options on the Postgres container.
2.  Start up the stack with `docker-compose up`. The `docs` and `livesync` containers will immediately close. This is
    expected. This will attach your terminal to their output, so you can close this and stop the containers with `Ctrl-C`.
3.  Restart the stack with `docker-compose up -d` to detach from the console after they've booted.
4.  Browse to `http://localhost` (or wherever this is living, if not localhost hostname has to match HOST setting), the site
    should be alive.
5.  Create the initial superuser from the command line. You can use this to log in from the webpage and get
    to the admin pages:
    ```
    docker-compose exec cores python3 manage.py createsuperuser
    ```

You'll end up with the following containers:

* **cores** - the core Django application, running as a WSGI endpoint
* **mkdocs** - builds these docs and dumps them into a volume for nginx to use
* **nginx** - WSGI server, also serves static assets and docs from volumes

If you want to see what a box is doing, run `docker-compose logs [container]` to view its logs.

For more information on the containers, see [Docker build scripts](../../docker-compose).
