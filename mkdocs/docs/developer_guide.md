Project overview
===

As mentioned in the overview, this project has three 'apps' or modules. For more info on the Django
achitecture that has led to this setup, take a look at the docs [here](https://docs.djangoproject.com/en/2.2/ref/applications/#projects-and-applications).

The idea is that although modules can *read from each other* they *never write to each others'* 
database objects. One exception of this is the API module. The Inventory module should be able to
operate standalone and has no dependencies on any other modules.

    +-------------------------+ +-------------------------+ +------------------------+
    |                         | |                         | |                        |
    |       Inventory         | |         Booking         | |       API (DRF)        |
    |                         | |                         | |                        |
    +-------------------------+ +-------------------------+ +------------------------+
    |                         | |                         | |                        |
    | * Database of objects   | | * Works with "bookables"| | * Config for           |
    |   and locations         | |   (handles on hosts to  | |   Django REST Framework|
    |                         | |   manage bookings       | |                        |
    | * Host specs, IPAM and  | |                         | | * All views generated  |
    |   status tracking       | | * Booking and           | |   automatically by DRF |
    |                         | |   reservation mgmt.     | |                        |
    | * Full API access on    | |                         | | * No models of its own |
    |   /API                  | |                         | |                        |
    |                         | |                         | |                        |
    +-------------------------+ +-------------------------+ +------------------------+

    +-------------------------+ +-------------------------+ +------------------------+
    |                         | |                         | |                        |
    |        Notices          | |          Live           | |         Loans          |
    |                         | |                         | |                        |
    +-------------------------+ +-------------------------+ +------------------------+
    |                         | |                         | |                        |
    | * Basic messages to     | | * Ingests MAC/IP map    | | * Very basic, just     |
    |   appear on dashboard   | |   from livescan         | |   a few models for     |
    |                         | |                         | |   tracking loans       |
    | * Target group, style,  | | * Creates ScanConflicts | |                        |
    |   priority, expiry      | |   if scan data suggests | | * No front-end         |
    |                         | |   inventory data is     | |   components           |
    |                         | |   incorrect             | |                        |
    |                         | |                         | | * Updates related host |
    |                         | |                         | |   statuses on save     |
    +-------------------------+ +-------------------------+ +------------------------+


Within the model definition for each, there should be validation carried out under the `clean()`
and `save()` [signals](https://docs.djangoproject.com/en/2.2/topics/signals/). Various `ValidationError`s
should be raised if the model you're trying to create or modify has an issue. This has the bonus of 
meaning that the autogenerated forms handle all the validation for us! Neat.

There are also some database maintenance hooks, like keeping related objects up to date (stopping bookings 
for a bookable if its host is made inactive for example)

Project layout
---

The `Cores` directory contains the main Django app, however there are several additional directories
which contain additional Dockerfiles for supporting containers when used in a production environment.

This project uses multiple [apps within the one core project](https://docs.djangoproject.com/en/2.2/ref/applications/#projects-and-applications),
each logically seperated in the filesystem to hopefully improve maintainability, and keep strong boundaries on functionality
for each of these apps (or modules). Currently the three modules are `api`, `booking` and `inventory`. They all share the
same DB and access each others' models through imports.

    [project root]/
        cores/
            cores/                      # Main Django project directory
                templates/
                    www/                # Shared HTML for all components
                        _base.html      # Core template used by all pages
                        ...
                    registration/
                        login.html      # Non-admin login page template
                static/                 
                    css/                # Shared static resources (css/js/img)
                        ...             # served from /static
                    js/
                        ...
                    ...
                settings.py             # Main Django settings file
                urls.py                 # Primary routing definitions
                wsgi.py                 # Django WSGI support (not currently in use)
            
            [booking|inventory|notices|loans]/ # Booking / inventory / notices / loans 'app' files
                migrations/             # DB migrations
                models/                 # DB/ORM model definitions
                static/                 # app-specific static resources
                templates/
                    www/
                        [app]/          # app-specific html templates
                views/                  # view definitions
                admin.py                # Model registrations for /admin pages
                urls.py                 # app-specific routing
                cron_jobs.py            # tasks hooked into from the api /cron endpoints
                tests.py                # app-specific unit tests
            
            
            live/                       # Livesync 'app' files
                migrations/             # DB migrations
                models/                 # DB/ORM model definitions
                static/                 # app-specific static resources
                templates/
                    www/
                        booking/        # app-specific html templates
                views/                  # view definitions
                admin.py                # Model registrations for /admin pages
                urls.py                 # app-specific routing
                scanhandler.py          # function to handle incoming API requests
                                        #      - imported by the API app
                example-livescan.json   # example expected input for the /api/live/ingest endpoint
                cron_jobs.py            # tasks hooked into from the api /cron endpoints
                tests.py                # app-specific unit tests
            
            api/                        # API config (Django REST framework)
                templates/
                    rest_framework/     # app specific html templates
                views/                  
                    ...                 # custom API endpoints
                urls.py                 # routing
                viewsets.py             # DRF viewset definitions
                serializers.py          # DRF serializer definitions
                admin.py                # register auth token in admin pages

            Dockerfile                  # container build script
            manage.py                   # Django entry file
            start.sh                    # easy start for container
            nuke_db.sh                  # utility script to wipe sqlite, migrations, rebuild
            wait-for-it.sh              # utility script to wait for postgres to come up
        
        mkdocs/
            index.md                    # The documentation homepage.
            ...                         # Other markdown pages, images and other files.
        mkdocs.yml                      # Documentation configuration file.
        
        nginx/                          # nginx (WSGI) container files
            cores.conf                  # config (injected on build)
            Dockerfile                  # container build script

        docker-compose.template.yml     # Base compose file (edit me)

Inventory
---

This is the core app, with the following object types:

```
 - Buildings, Labs and Racks
 - Cards and Card Types (with option Host as parent and asset no, eg RAID card)
 - HdVendors
 - HostBuilds (OS build types)
 - HostHardwares (Hardware types, eg Sandybridge)
 - HostTypes (system type/role, eg tcpreplay)
 - Nics (MAC address, IP, lastseen)
 - Hosts
    - hostname
    - serial no & asset no
    - diskvendor, hardware, rack, type and build (as foreign keys)
    - vm host (fk to parent host if virtualised)
    - hypervisor bool (if vm host)
    - status (from an enum)
    - IP and lastseen, automatically updated on save of NICs
    - reverse accessors to:
        - NICs (with options to set primary nic and role)
        - Cards
```

Currently it relies on the autogenerated Django admin pages (/admin) for all the
data management. These seem really nice, so it will likely only be reporting that
recieves custom views on the frontend. See a screenshot of the [host editor page](img/admin_host_edit.png) 
or the [NIC list](img/admin_nic_list.png)

Booking
---

This provides the majority of the actual functionality to the project, and has its own DB models
to help keep track of things, and *keep the booking info out of the inventory tables*.

```
 - Bookable
    - Status (from enum, ['created', 'active', 'suspended', 'inactive'])
    - Host as fk
    - Comment
    - Reverse accessors to 'bookings' and 'reservations'

 - [Booking | Reservation]
    - Bookable as fk
    - Owner as fk
    - Booking start and end DateTimes
    - Project as fk
    - Comment
    - Timestamp (autogenerated on create)
```

There is a lot of validation logic in these models, and a good number of helper functions
to try to make keeping the schedule valid as easy as possible. Some helpers of note are:

```python
# is this host free at a specific time? If not, give me the booking at that time
Bookable.check_free(when=timezone.now())

# check if the host is reserved, optionally ignoring a specific reservation (for editing entries)
Bookable.check_reserved(ignore=None)

# get this bookable's future bookings/reservations as a queryset
Bookable.get_calendar()
Bookable.get_reservations()
```

Reservations are created without an end time and are ended by adding an end time. Reservations
can be created with a start time in the future (to allow you to get a reservation in ahead of
any future bookings coming in) and everything should work as you'd expect.


Notices
---

Barely worthy of its own section, its a really simple model that gets pulled in from the booking
dashboard. Managed through the Admin pages as well. You can set expiry dates if you want messages to
automatically dissapear, all calculated on the fly. Users and groups are pulled from the core
Django authentication module.

!!! note
    Expired messages won't be automatically deleted, this could probably benefit from a maintenance/
    cleanup script, like quite a lot of this app.

API
---

This is using the [Django REST Framework](https://www.django-rest-framework.org/). Everything is
very straightforward, pretty much at the moment all of the Inventory models have been implemented
as described in the [example](https://www.django-rest-framework.org/#example).

!!! tip
    Handily, it provides a rather nice web interface for the API, letting you easily make requests from
    the browser. Just visit any endpoint from a browser and you'll be given that instead.

Serializers have been moved into their own file, as have the classviews. A few of the classviews have had
their `get_queryset()` function overridden to support filtering based on GET parameters.

There a couple of endpoints (for the livesync) that are running on custom views, these import functions
from the live app.

DRF has also been configured to use [`LimitOffsetPagination`](https://www.django-rest-framework.org/api-guide/pagination/#limitoffsetpagination), 
eg `GET https://api.example.org/accounts/?limit=100&offset=400`.

### Authentication

Auth is currently readonly for anonymous users, otherwise it uses your Django account permissions. 
There is also token based authentication, keys can be generated from the admin pages.

> "For clients to authenticate, the token key should be included in the `Authorization` HTTP header. 
> The key should be prefixed by the string literal "Token", with whitespace separating the two strings. 
> For example:
>
> `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`"
>
> *From [DRF docs](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)*

!!! warning
    Of course we have zero actual security as this is being deployed over HTTP, but ¯\\_(ツ)_/¯

Live
---

This module handles ingest of livescan data. There is an API endpoint registered in the API app that points
to the live `scanhandler.py:ingest` function. This accepts a JSON of the following format:

```json
{
    "agentident": "<id of agent performing the scan>",
    "timestamp": "<python datetime string>",
    "results": [
        {
            "nic": "<nic db id>",
            "ip": "<ip>"
        },
        {
            "mac": "<mac address>",
            "ip": "<ip>"
        }
    ]
}
```

Simply, it takes a mapping of IP addresses to either MAC addresses or database NIC IDs. The agent identifier is
used to flag where this scan came from in the admin panel, and along with the timestamp, prevent duplicate scan 
data from being processed.

The data is then compared against what we have in the inventory (if the nic exists) and conflicts are created if
there's something different.

!!! tip
    The ingest is processed when the model is saved, so you can manually add entries via the admin pages. Note that
    the `raw_data` field contains the results datastructure as valid JSON.

### ScanConflicts

These are based around the core `ScanConflict` model, which inherits from [Django-polymorphic](https://django-polymorphic.readthedocs.io/en/stable/)'s
`PolymorphicModel`. This allows this model to be shared by the following types of conflict as their base
class:

* `NicScanConflict` - IP address conflicts
* `LocationScanConflict` - location (from lab subnet definitions) conflict, can include tagged NIC conflict and 
                    suggested new location
* `UnknownScanConflict` - we've found a MAC that doesn't exist in the database

These also have some fun tweaks to make them work sort of sensibly in Django admin, thankfully the project includes
lots of help for that in their [docs](https://django-polymorphic.readthedocs.io/en/stable/admin.html).

There is also a final model in this app, called `VirtualHostScan`. This sort of a type of `UnknownScanConflict` for MAC
addresses that are set with the [locally administered bit](https://en.wikipedia.org/wiki/MAC_address#/media/File:MAC-48_Address.svg)
to be true, which signifies this is a virtual machine. It allows us to display them in the Host IP address list without
needing to create unnecessary conflicts or inventory entries, as these aren't managed centrally nor are particularly
long-lived.

### Scan Handler

The `scanhandler.py` holds the logic for ingesting scan data. Each request is stored as a `ScanSession` along
with a timestamp (either that from the request or current server time if that's missing), and conflicts from each
session are tied to their session with a foreign key.

The process is roughly as follows:

1. If there's a timestamp in the request, check if there's a `ScanSession` with the same agent identifier 
   and timestamp. If there is, error out and refuse the data.
2. Create a new `ScanSession` object.
3. For each entry in the request's 'results' array:
    1. Try to find a NIC with the same MAC or ID, if not, create an `UnknownScanConflict`.
        - If the MAC is has its locally administered bit set, we update or create a `VirtualHostScan` object
          instead.
    2. Check if the NIC IP in the database matches, if not:
        1. If the NIC has a host and the host is 'new' and there is no existing IP, accept the new IP and set the
          host status to 'active'
        2. Otherwise, check if there's any existing `NicScanConflict` objects for that host that
          are 'new' or 'ignored', if any of these hold the same data as the new conflict, don't bother
          creating a new one, if they are different, mark the old scan conflicts as 'super'(seded).
        3. If the NIC has a host:
            - If there is an existing rack, check to see if the new IP is within the existing lab's subnet, 
              otherwise create a `LocationScanConflict`, again with deduplication.
            - If there isn't an existing rack, try to find which lab it should be in. If the detected new lab
              has a rack 0 (default rack), just update the host to be in the default rack.
            - Otherwise, check for existing conflicts, and create a `LocationScanConflict` for the host with the
              suggested new lab if one has been found. 
    3. Update the lastseen for the NIC (which will automatically update the host through the model save signal)
    4. Append a little status report for that NIC to the response.
4. Add the full list of responses to the `ScanSession` and mark it as processed, save the session and return those
   status responses.

Loans
---

Very simple couple of models, to give admins a way to keep track of whether hosts have been put on loan. There's no
frontend for this, all management is through the admin panel (for the time being). Only semblance of cleverness is
if a host is put on loan, its inventory record will be updated as "on loan" and its bookable (if there is one) will
be suspended.

Scheduled jobs
---

There are a few things that need to run on a schedule for this app, to save having a bunch of awkward task scheduling/
event brokering plugins in Django, we've just got a couple of API endpoints being hit by a `curl` request from a cron
job, which triggers the necessary scripts.

Currently these are split into two categories:

* **morningJobs**: `/api/cron/morningjobs`
    These are scheduled to run every morning, and are (hopefully) fairly short jobs, currently only used by Booking for working 
    out what bookings are starting/ending today and sending out some notification emails. This only needs to be hit once a day, 
    but it won't spam people if it keeps getting hit.

* **maintenanceJobs**: `/api/cron/maintenance`
    These are potentially slower tasks, the cron endpoint is hit out of hours and it's currently used for clearing up old expired
    notices, old inactive ScanSessions and old bookings that have already happened.

!!! info
    The general rule that has been used is that stuff will be kept for 3 months, if it's not active it will then be deleted.

### Cron source

In the Docker stack, the `livesync` container has an extra couple of entries in its crontab to hit these endpoints. It saved
having Cron running on another container just to handle this, however all they need is a POST request to them:

```sh
23 8 * * * curl -X POST http://nginx/api/cron/morningjobs
23 3 * * * curl -X POST http://nginx/api/cron/maintenance
```

Unit tests
---

This app has a light sprinkling of unit tests to cover the main model validation, ingest, maintenance and notification functions
all using the built in Django test client.

You'll need a DB connection set up, but other than that you can run the test suite with:

```
python3 manage.py test
```

The test client spins up a new DB, pre-populates and tears it all down afterwards. If you want to keep the DB between tests (saves
some time during development), just add `--keepdb` to the command.
