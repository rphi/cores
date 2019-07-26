User guide
===

!!! info
    Management of the inventory, users and other administration tasks is carried out via the 
    admin interface. That's all covered in the [admin guide](../admin_guide)

Creating a Booking/Reservation
---

You want to book a thing? Neat. Let's go. This is the booking dashboard:

![booking dashboard](img/dashboard.png)

This shows you any notices, your upcoming bookings and reservations and any machines that are
available to book right now. You can cancel your bookings and reservations from here if you need
to.

To view the full bookables listing there's a button for that.

![bookable list](img/bookable_list.png)

You can see all machines with bookables here, with fitlering options. Anything with a green button is 
available to book now, red means it's currently booked, but you can still book or reserve it for later, 
orange means it's currently reserved and grey means suspended. Results are loaded 50 at a time, with an
option to load more at the bottom of the table.

Filter options are added to the URL "hash" and to your browser history, so your back button works as
expected, and you can share or bookmark a URL like the following to have your exact query spring
straight back to life:

```
http://cores/booking/search/#nores=1&mygroup=1&free=1&lab=3,4,5,7&hw=12,10,11,13,21,22,23
```

!!! note
    Those hash parameters correspond directly to HTTP GET parameters on the `/api/booking/bookable` 
    endpoint used to populate the booking table.

Click any of the buttons to go to the host info page, where you can see some more specs about the
host, a rough availability timeline and listings of upcoming bookings and reservations.

![host details](img/host.png)

If you'd like to go ahead and book or reserve, mash the button in the top right. The system
will ask you for some more details, check everything checks out and create that for you.

!!! warning "Heads up..."
    Not all users have permissions to reserve a host, if you don't have permission you can ask
    another user to create the reservation and assign it to you.

Managing Live Scan Conflicts
---

When live ARP mappings are pushed in by the [Livesync](../livesync) component, Cores will compare this 
to the information it has in its database and create `ScanConflict` objects if there are any mismatches.

![livescan dashboard](img/livescan_dash.png)

Conflicts can currently be of three types:

  - `NicScanConflict`: we've seen another IP for that NIC's mac address
  - `LocationScanConflict`: the new IP for that host's NIC implies it has moved to a new Lab
  - `UnknownScanConflict`: we haven't seen this mac on the network before, and it isn't in our inventory

!!! info
    This section is only accessible to users with the 'View ScanConflict' permission.

For NIC (IP address) conflicts, Cores offers to accept this change and automatically update the NIC in
question. For Location conflicts, you can enter a quickfix page to confirm the new location, assign
the host a rack number and again update the host.

All conflicts have the options to "Mark resolved" or "Ignore". If a conflict is marked resolved it will
dissapear from the list, but be re-generated if the conflict occurs again. If the conflict is ignored,
it will again be removed from the list but not resurface even if the conflict occurs again in the next
scan, until the conflict is cleared from the database (if using the [maintenance cron](../developer_guide/#scheduled-jobs),
this will be after three months).

If a scan conflict is resolved externally, it should be resolved on the next scan or as part of the 
maintenance cron and removed from the conflicts dashboard automatically.
