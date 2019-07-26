Administration guide
===

Getting a copy up and running
---

You've got two options, a [local instance of Django](../setup/local_development) using its built-in development server 
(great for debugging with auto-reloading), or the production-ready [Docker stack](../setup/production_docker_deployment/).

Django admin pages
---

One of the best bits of Django is that it will put together a rather decent admin panel to
let you manage all your models, assuming they are written correctly, and run any custom validation
code for you as well.

For more info on the admin site, feel free to give the [Django docs](https://docs.djangoproject.com/en/2.2/ref/contrib/admin/)
on the matter a quick read.

You can get to the admin pages from `/admin` or the admin link in the navbar. You'll need to be logged
in and have staff status set on your account. Pretty much all of the administration is from this
interface.

The homepage is organised by app, then by database model.

![admin homepage](img/admin_home.png)

That's a great segway into...

User management
---

!!! info
    By default, there will be no users in the database, meaning you won't be able to log in to create any users!
    To get the initial superuser set up, from the terminal of the host that's running 
    the project, run the following to set yourself a superuser account: `python3 manage.py createsuperuser`
    
    Or if you're running this in Docker: `docker-compose exec cores bash` followed by `python3 manage.py createsuperuser`

    This should get you into the admin panel and let you start setting up other users and their permissions.

![admin panel user list](img/admin_userlist.png)

### Permissions

Currently you don't need to be logged in to read system info and see booking status, however if you want to book something 
you will be asked to login. You will need to be marked as a 'staff member' to have access to the `/admin` pages.  If 
you're trying to reserve something, you'll need the `booking.add_reservation` permission. You also need 
`live.view_scanconflict` to view the live pages, and `live.change_scanconflict` to action on them.

All permissions are managed through the Django admin users and groups.

### Impersonation

!!! info
    This feature is only available to users with "staff" permissions. (can access admin pages)

If you need to test something from the perspective of another user, it is possible to temporarily impersonate them. This
is achieved using the [django-impersonate](https://pypi.org/project/django-impersonate/) plugin.

To start a session, visit a user's page (/booking/user/id/detail) and choose the button. You will only see this if you
have permission to start a session. An orange "Impersonating" button will appear next to the logout button, and you will
be authenticated as the user you've selected. Click this button to end your session and return to your own identity.

There are a few other endpoints exposed by the plugin:

  - `/impersonate/<user-id>/` - impersonate user by ID
  - `/impersonate/stop/` - end session
  - `/impersonate/list/` - list all users
  - `/impersonate/search/` - search users

All sessions are logged.

Populating the inventory
---

Generally, you should be able to just open the Hosts node in the admin panel, and start filling in the details. 
If the field you are trying to fill is expecting a foreign key, it will offer a dropdown, and the option to create
a new item of that type. You can also populate each of the individual components independently if you feel like it.

![admin panel adding a host](img/admin_host_edit.png)

Fingers crossed, everything here should be validated on save, so you shouldn't be able to break the database!

!!! question "Why aren't my new hosts appearing in the bookable hosts list?"
    To keep the databases a little seperate from each other, the hosts won't be bookable until we've created a 
    Bookable for them and made it active.

Creating bookables
---

Once you've got your hosts in the inventory, you'll need to hop back to the admin homepage, and create a Bookable 
for each host that you want to appear in the bookable list. You will also need to ensure that the status is set to
'Active' for it to be bookable.

!!! tip
    You can also create bookables in bulk from the bulk actions menu on the hosts list, and mark bookables as active
    in bulk from the bookable list.

Managing bookings and reservations
---

Again, this all should be pretty self explanatory. You can create and delete bookings and reservations here if you need to,
all the validation logic should run as usual. With regards to reservations, these should be created without an end time, 
then the end time set once the reservation has finished.

!!! question "Can users end their own reservations?"
    Simple answer, **no**. You will need to add an end time as now to the reservation to mark it as finished. They can
    however cancel reservations if they have yet to start.

Backups
---

The easiest way to grab a full state backup of Cores is to get a dump from the Postgres DB. Handily, the `pg_dump` is a 
command that exists solely for this purpose!

Just run the following on your host to create that backup:

```sh
docker-compose exec postgres pg_dump -U django cores > "./cores_dump_$(date +"%Y_%m_%d").pgsql"
```

For more information on `pg_dump` and how to re-import this file, please see the [Postgres docs](https://www.postgresql.org/docs/6.4/app-pg-dump.htm)

!!! warning
    This doesn't backup the secret key from the `docker-compose.yml` environment variables. Saying that, the secret key
    isn't used for much beyond transitory stuff (session cookies, CSRF tokens and the like) so you shouldn't have much
    issue beyond everyone being logged out if you change that.
