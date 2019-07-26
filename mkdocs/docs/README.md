This is Cores
===

Cores is a new toolkit for managing the labs, incorporating inventory management and device booking. It is built on
Python and [Django](https://www.djangoproject.com/).

![host](img/dashboard.png)

Features
---

* **Inventory management** - asset database for hosts, serial and asset support, location tracking, owner and group
            tracking. Integration with Livesync for last-seen times.
* **Lab Booking** - booking and reservation of machines, through self-service frontend. Reporting on utilisation,
            restrictions by group.
* **Notices** - quick noticeboard on the booking dashboard for users.
* **Livesync** - ingest of MAC/IP mappings with detection and alerting for IP address and location changes.

!!! question "Where next?"
    Get started setting up a copy with the [admin guide](admin_guide) or start booking things with the 
    [user guide](user_guide).

About this app
---

This was developed over June/July 2019 to replace the existing booking system with something based on open technologies
by Robert Phipps ([_rphi](https://rphi.uk)) as a summer placement project.
