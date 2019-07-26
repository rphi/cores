from django.core.mail import send_mail, EmailMessage
from os import getenv

def send_booking_confirmation(booking):
    if not getenv('SMTP_SERVER'):
        print("SMTP disabled, not sending email.")
        return
    send_mail(
        subject=f"Booking for {booking.bookable.host} to start at {booking.start} confirmed",
        message=f"""Hi {booking.owner.first_name}, your booking for {booking.bookable.host} starting at {booking.start} and finishing at {booking.end} has been
            successfully created.""",
        html_message=f"""<p>Hi {booking.owner.first_name},</p>
            <p>Your booking for {booking.bookable.host} starting at {booking.start} and finishing at {booking.end} has been
            successfully created.</p>

            <p>You have booked a {booking.bookable.host.hardware} with IP address {booking.bookable.host.ip} 
            in {booking.bookable.host.rack}.</p>

            <p>You can view more information about the host you've booked <a href="http://{getenv('HOSTNAME')}/booking/host/{booking.bookable.id}">here</a>.</p>

            <p>To manage your bookings, log into <a href="http://{getenv('HOSTNAME')}/booking/">Cores</a></p>""",
        from_email=getenv('SMTP_FROM'),
        recipient_list=[booking.owner.email]
    )

def send_reservation_cancellation(reservation):
    if not getenv('SMTP_SERVER'):
        print("SMTP disabled, not sending email.")
        return
    send_mail(
        subject=f"Reservation for {reservation.bookable.host} to start at {reservation.start} cancelled",
        message=f"""Hi {reservation.owner.first_name}, your booking for {reservation.bookable.host} due to start at {reservation.start} has been
            successfully cancelled.""",
        html_message=f"""<p>Hi {reservation.owner.first_name},</p>
            <p>Your booking for {reservation.bookable.host} due to start at {reservation.start} has been
            successfully cancelled.</p>

            <p>You had booked a {reservation.bookable.host.hardware} with IP address {reservation.bookable.host.ip} 
            in {reservation.bookable.host.rack}.</p>

            <p>You can view more information about the host you had booked <a href="http://{getenv('HOSTNAME')}/booking/host/{reservation.bookable.id}">here</a>.</p>

            <p>To manage your bookings, log into <a href="http://{getenv('HOSTNAME')}/booking/">Cores</a></p>""",
        from_email=getenv('SMTP_FROM'),
        recipient_list=[reservation.owner.email]
    )

def send_booking_cancellation(booking):
    if not getenv('SMTP_SERVER'):
        print("SMTP disabled, not sending email.")
        return
    send_mail(
        subject=f"Booking for {booking.bookable.host} to start at {booking.start} cancelled",
        message=f"""Hi {booking.owner.first_name}, your booking for {booking.bookable.host} due to start at {booking.start} and finishing at {booking.end} has been
            successfully cancelled.""",
        html_message=f"""<p>Hi {booking.owner.first_name},</p>
            <p>Your booking for {booking.bookable.host} due to start at {booking.start} and finishing at {booking.end} has been
            successfully cancelled.</p>

            <p>You had booked a {booking.bookable.host.hardware} with IP address {booking.bookable.host.ip} 
            in {booking.bookable.host.rack}.</p>

            <p>You can view more information about the host you had booked <a href="http://{getenv('HOSTNAME')}/booking/host/{booking.bookable.id}">here</a>.</p>

            <p>To manage your bookings, log into <a href="http://{getenv('HOSTNAME')}/booking/">Cores</a></p>""",
        from_email=getenv('SMTP_FROM'),
        recipient_list=[booking.owner.email]
    )

def send_reservation_confirmation(reservation):
    if not getenv('SMTP_SERVER'):
        print("SMTP disabled, not sending email.")
        return
    send_mail(
        subject=f"Reservation for {reservation.bookable.host} to start at {reservation.start} confirmed",
        message=f"""Hi {reservation.owner.first_name}, your reservation for {reservation.bookable.host} starting at {reservation.start} has been
            successfully created.""",
        html_message=f"""<p>Hi {reservation.owner.first_name},</p>
            <p>Your reservation for {reservation.bookable.host} starting at {reservation.start} has been
            successfully created.</p>

            <p>You have reserved a {reservation.bookable.host.hardware} with IP address {reservation.bookable.host.ip} 
            in {reservation.bookable.host.rack}.</p>

            <p>You can view more information about the host you've reserved <a href="http://{getenv('HOSTNAME')}/booking/host/{reservation.bookable.id}">here</a>.</p>

            <p>To manage your bookings, log into <a href="http://{getenv('HOSTNAME')}/booking/">Cores</a></p>""",
        from_email=getenv('SMTP_FROM'),
        recipient_list=[reservation.owner.email]
    )

def send_inactive_bookable(booking):
    if not getenv('SMTP_SERVER'):
        print("SMTP disabled, not sending email.")
        return
    send_mail(
        subject=f"Update regarding your booking: {booking.bookable.host} is no longer available",
        message=f"""Hi {booking.owner.first_name}, this is regarding your booking/reservation for {booking.bookable.host} starting {booking.start}.

The host {booking.bookable.host} has been marked as '{booking.bookable.status}', so may no longer be available.
Please contact a lab admin to confirm what has happened.""",
        html_message=f"""<p>Hi {booking.owner.first_name},</p>
            <p>This is regarding your booking/reservation for {booking.bookable.host} starting {booking.start}</p>

            <p>The host {booking.bookable.host} has been marked as '{booking.bookable.status}' with a host status of '{booking.bookable.host.status}', so may no longer be available.
            Please contact a lab admin to confirm what has happened.</p>

            <p>You have booked/reserved a {booking.bookable.host.hardware} with IP address {booking.bookable.host.ip} 
            in {booking.bookable.host.rack}.</p>

            <p>You can view more information about the host you've booked <a href="http://{getenv('HOSTNAME')}/booking/host/{booking.bookable.id}">here</a>.</p>

            <p>To manage your bookings, log into <a href="http://{getenv('HOSTNAME')}/booking/">Cores</a></p>""",
        from_email=getenv('SMTP_FROM'),
        recipient_list=[booking.owner.email]
    )

def send_reservation_reminder(reservation):
    if not getenv('SMTP_SERVER'):
        print("SMTP disabled, not sending email.")
        return
    send_mail(
        subject=f"Reminder: reservation for {reservation.bookable.host} to start at {reservation.start}",
        message=f"""Hi {reservation.owner.first_name}, your reservation for {reservation.bookable.host} is starting at {reservation.start}.""",
        html_message=f"""<p>Hi {reservation.owner.first_name},</p>
            <p>Your reservation for {reservation.bookable.host} is starting at {reservation.start}.</p>

            <p>You have booked a {reservation.bookable.host.hardware} with IP address {reservation.bookable.host.ip} 
            in {reservation.bookable.host.rack}.</p>

            <p>If you no longer need this booking, you can cancel it <a href="http://{getenv('HOSTNAME')}/booking/cancel/r/{reservation.id}">here</a>.
            You can view more information about the host you've booked <a href="http://{getenv('HOSTNAME')}/booking/host/{reservation.bookable.id}">here</a>.</p>

            <p>To manage your bookings, log into <a href="http://{getenv('HOSTNAME')}/booking/">Cores</a></p>""",
        from_email=getenv('SMTP_FROM'),
        recipient_list=[reservation.owner.email]
    )

def send_booking_reminder(booking):
    if not getenv('SMTP_SERVER'):
        print("SMTP disabled, not sending email.")
        return
    send_mail(
        subject=f"Reminder: booking for {booking.bookable.host} to start at {booking.start}",
        message=f"""Hi {booking.owner.first_name}, your booking for {booking.bookable.host} is starting at {booking.start}.""",
        html_message=f"""<p>Hi {booking.owner.first_name},</p>
            <p>Your booking for {booking.bookable.host} is starting at {booking.start}.</p>

            <p>You have booked a {booking.bookable.host.hardware} with IP address {booking.bookable.host.ip} 
            in {booking.bookable.host.rack}. Your booking will finish at {booking.end}</p>

            <p>If you no longer need this booking, you can cancel it <a href="http://{getenv('HOSTNAME')}/booking/cancel/b/{booking.id}">here</a>.
            You can view more information about the host you've booked <a href="http://{getenv('HOSTNAME')}/booking/host/{booking.bookable.id}">here</a>.</p>

            <p>To manage your bookings, log into <a href="http://{getenv('HOSTNAME')}/booking/">Cores</a></p>""",
        from_email=getenv('SMTP_FROM'),
        recipient_list=[booking.owner.email]
    )

def send_booking_reminder_last(booking, last_booking):
    if not getenv('SMTP_SERVER'):
        print("SMTP disabled, not sending email.")
        return
    send_mail(
        subject=f"Reminder: booking for {booking.bookable.host} to start at {booking.start}",
        message=f"""Hi {booking.owner.first_name}, your booking for {booking.bookable.host} is starting at {booking.start}.""",
        html_message=f"""<p>Hi {booking.owner.first_name},</p>
            <p>Your booking for {booking.bookable.host} is starting at {booking.start}.</p>

            <p>The last owner of this booking was {last_booking.owner.get_full_name()} and their booking ended {last_booking.end}</p>

            <p>You have booked a {booking.bookable.host.hardware} with IP address {booking.bookable.host.ip} 
            in {booking.bookable.host.rack}. Your booking will finish at {booking.end}</p>

            <p>If you no longer need this booking, you can cancel it <a href="http://{getenv('HOSTNAME')}/booking/cancel/b/{booking.id}">here</a>.
            You can view more information about the host you've booked <a href="http://{getenv('HOSTNAME')}/booking/host/{booking.bookable.id}">here</a>.</p>

            <p>To manage your bookings, log into <a href="http://{getenv('HOSTNAME')}/booking/">Cores</a></p>""",
        from_email=getenv('SMTP_FROM'),
        recipient_list=[booking.owner.email]
    )


def send_booking_ending(booking):
    if not getenv('SMTP_SERVER'):
        print("SMTP disabled, not sending email.")
        return
    send_mail(
        subject=f"Reminder: booking for {booking.bookable.host} is ending soon",
        message=f"""Hi {booking.owner.first_name}, your booking for {booking.bookable.host} is due to finish at {booking.end}.""",
        html_message=f"""<p>Hi {booking.owner.first_name},</p>
            <p>Your booking for {booking.bookable.host} is due to finish at {booking.end}.</p>

            <p>You have booked a {booking.bookable.host.hardware} with IP address {booking.bookable.host.ip} 
            in {booking.bookable.host.rack}.</p>

            <p>If you still require this machine, you may be able to extend your booking <a href="http://{getenv('HOSTNAME')}/booking/host/{booking.bookable.id}/book">here</a>.
            You can view more information about the host you've booked <a href="http://{getenv('HOSTNAME')}/booking/host/{booking.bookable.id}">here</a>.</p>

            <p>To manage your bookings, log into <a href="http://{getenv('HOSTNAME')}/booking/">Cores</a></p>""",
        from_email=getenv('SMTP_FROM'),
        recipient_list=[booking.owner.email]
    )

def send_booking_ending_hard(booking, nextbooking):
    if not getenv('SMTP_SERVER'):
        print("SMTP disabled, not sending email.")
        return
    send_mail(
        subject=f"Reminder: you will lose access to {booking.bookable.host} soon",
        message=f"""Hi {booking.owner.first_name}, your booking for {booking.bookable.host} is due to finish at {booking.end}, and that device is booked by 
{nextbooking.owner.get_full_name()}<{nextbooking.owner.email}> from {nextbooking.start}. Please ensure you have cleared all 
important data off this machine before your booking ends.""",
        html_message=f"""
            <p>Hi {booking.owner.first_name},</p>
            <p>Your booking for {booking.bookable.host} is due to finish at {booking.end}, and that device is booked by 
            <a href="mailto:{nextbooking.owner.email}">{nextbooking.owner.get_full_name()}</a> from {nextbooking.start}.</p>

            <p><strong>Please ensure you have cleared all important data off this machine before your booking ends.</strong>. Alternatively, contact
            <a href="mailto:{nextbooking.owner.email}">{nextbooking.owner.get_full_name()}</a> to arrange a possible extension.</p>

            <p>You have booked a {booking.bookable.host.hardware} with IP address {booking.bookable.host.ip} 
            in {booking.bookable.host.rack}.</p>

            <p>You can view more information about the host you've booked <a href="http://{getenv('HOSTNAME')}/booking/host/{booking.bookable.id}">here</a>.</p>

            <p>To manage your bookings, log into <a href="http://{getenv('HOSTNAME')}/booking/">Cores</a></p>""",
        from_email=getenv('SMTP_FROM'),
        recipient_list=[booking.owner.email]
    )

def send_booking_ended(booking):
    if not getenv('SMTP_SERVER'):
        print("SMTP disabled, not sending email.")
        return
    send_mail(
        subject=f"Booking for {booking.bookable.host} has ended",
        message=f"""Hi {booking.owner.first_name}, your booking for {booking.bookable.host} finished at {booking.end}. Please re-book
this machine if you'd like to continue using it: http://{getenv('HOSTNAME')}/booking/host/{booking.bookable.id}/book

This host is now available for booking again, ensure that you have copied everything you need off this machine.""",
        html_message=f"""<p>Hi {booking.owner.first_name},</p>
            <p>Your booking for {booking.bookable.host} finished at {booking.end}. Please <a href="http://{getenv('HOSTNAME')}/booking/host/{booking.bookable.id}/book">re-book</a>
            this machine if you'd like to continue using it.</p>
                        
            <p>You had booked a {booking.bookable.host.hardware} with IP address {booking.bookable.host.ip} 
            in {booking.bookable.host.rack}.</p>
                        
            <p>To manage your bookings, log into <a href="http://{getenv('HOSTNAME')}/booking/">Cores</a></p>""",
        from_email=getenv('SMTP_FROM'),
        recipient_list=[booking.owner.email]
    )

def send_booking_ended_hard(booking, nextbooking):
    if not getenv('SMTP_SERVER'):
        print("SMTP disabled, not sending email.")
        return
    send_mail(
        subject=f"Booking for {booking.bookable.host} has ended",
        message=f"""Hi {booking.owner.first_name}, your booking for {booking.bookable.host} finished at {booking.end}. Please re-book
this machine if you'd like to continue using it: http://{getenv('HOSTNAME')}/booking/host/{booking.bookable.id}/book

This host is now available for booking again, ensure that you have copied everything you need off this machine.""",
        html_message=f"""<p>Hi {booking.owner.first_name},</p>
            <p>Your booking for {booking.bookable.host} finished at {booking.end}. and that device is booked by 
            <a href="mailto:{nextbooking.owner.email}">{nextbooking.owner.get_full_name()}</a> from {nextbooking.start}.</p>

            <p><strong>Please ensure you have cleared all important data off this machine before your booking ends.</strong>. Alternatively, contact
            <a href="mailto:{nextbooking.owner.email}">{nextbooking.owner.get_full_name()}</a> to arrange a possible extension.</p>
                        
            <p>You had booked a {booking.bookable.host.hardware} with IP address {booking.bookable.host.ip} 
            in {booking.bookable.host.rack}.</p>
                        
            <p>To manage your bookings, log into <a href="http://{getenv('HOSTNAME')}/booking/">Cores</a></p>""",
        from_email=getenv('SMTP_FROM'),
        recipient_list=[booking.owner.email]
    )

def send_reservation_ended(reservation, nextbooking):
    if not getenv('SMTP_SERVER'):
        print("SMTP disabled, not sending email.")
        return
    send_mail(
        subject=f"Reservation for {reservation.bookable.host} has ended",
        message=f"""Hi {reservation.owner.first_name}, your reservation for {reservation.bookable.host} has been ended at {reservation.end}. Please re-book
this machine if you'd like to continue using it: http://{getenv('HOSTNAME')}/booking/host/{reservation.bookable.id}/book

The next booking for {nextbooking.owner.get_full_name()}<{nextbooking.user.email}> is due to start at {nextbooking.start}. Please ensure
you have everything you need off this machine.""",
        html_message=f"""<p>Hi {reservation.owner.first_name},</p>
            <p>Your reservation for {reservation.bookable.host} finished at {reservation.end}. Please <a href="http://{getenv('HOSTNAME')}/booking/host/{reservation.bookable.id}/book">re-book</a>
            this machine if you'd like to continue using it.</p>

            <p>The next booking for <a href="mailto:{nextbooking.user.email}">{nextbooking.owner.get_full_name()}</a> is due to start at {nextbooking.start}. Please ensure
            you have everything you need off this machine.</p>
                        
            <p>You had reservation a {reservation.bookable.host.hardware} with IP address {reservation.bookable.host.ip} 
            in {reservation.bookable.host.rack}.</p>
                        
            <p>To manage your bookings, log into <a href="http://{getenv('HOSTNAME')}/booking/">Cores</a></p>""",
        from_email=getenv('SMTP_FROM'),
        recipient_list=[reservation.owner.email]
    )

def send_reservation_nag(reservation):
    if not getenv('SMTP_SERVER'):
        print("SMTP disabled, not sending email.")
        return
    send_mail(
        subject=f"Reminder: you have {reservation.bookable.host} reserved",
        message=f"""Hi {reservation.owner.first_name}, you have an active reservation for {reservation.bookable.host} which you have had reserved since {reservation.start}
Do you still need this machine? If not, please let a lab admin know so that it can be released.""",
        html_message=f"""
            <p>Hi {reservation.owner.first_name},</p>
            <p>You have an active reservation for {reservation.bookable.host} which you have had reserved since {reservation.start}</p>

            <p><strong>Do you still need this machine?</strong> If not, please let a lab admin know so that it can be released.</p>

            <p>You have reserved a {reservation.bookable.host.hardware} with IP address {reservation.bookable.host.ip} 
            in {reservation.bookable.host.rack}.</p>

            <p>You can view more information about the host you've booked <a href="http://{getenv('HOSTNAME')}/booking/host/{reservation.bookable.id}">here</a>.</p>

            <p>To manage your bookings, log into <a href="http://{getenv('HOSTNAME')}/booking/">Cores</a></p>""",
        from_email=getenv('SMTP_FROM'),
        recipient_list=[reservation.owner.email]
    )
