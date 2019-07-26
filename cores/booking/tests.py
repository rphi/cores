from django.test import TestCase
import unittest
from .models import Bookable, Booking, Reservation
from inventory.models import Host, HostType, HostHardware
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils.timezone import make_aware, now
from django.core.exceptions import ValidationError
from django.core import mail

# Create your tests here.

class BookingTests(TestCase):
    @classmethod
    def setUpTestData(self):
        ht = HostType(name="test")
        ht.save()
        hh = HostHardware(name="test", host_type=ht)
        hh.save()
        self.hh = hh
        h = Host(hostname="test", hardware=hh)
        h.save()
        b = Bookable(host=h, status="active")
        b.save()
        self.bookable = b
        self.host = h

        u = User(username="test", password="test")
        u.save()
        self.testuser = u

    def setUp(self):
        pass

    def test_subsequent_bookings(self):
        '''
        Creates two bookings, one after the other
        '''
        b1 = Booking(
            bookable = self.bookable,
            owner = self.testuser,
            start = make_aware(datetime(2019,7,20,0,0)),
            end = make_aware(datetime(2019,7,24,23,59,59)),
            comment = "automated test"
        )
        b1.save()

        b2 = Booking(
            bookable = self.bookable,
            owner = self.testuser,
            start = make_aware(datetime(2019,7,25,0,0)),
            end = make_aware(datetime(2019,7,27,23,59,59)),
            comment = "automated test"
        )
        b2.save()
        return True

    def test_overlapping_bookings(self):
        '''
        Creates two bookings, one overlapping the other
        '''
        b1 = Booking(
            bookable = self.bookable,
            owner = self.testuser,
            start = make_aware(datetime(2019,7,28,0,0)),
            end = make_aware(datetime(2019,7,29,23,59,59)),
            comment = "automated test"
        )
        b1.save()

        b2 = Booking(
            bookable = self.bookable,
            owner = self.testuser,
            start = make_aware(datetime(2019,7,29,0,0)),
            end = make_aware(datetime(2019,7,30,23,59,59)),
            comment = "automated test"
        )
        with self.assertRaises(ValidationError):
            b2.save()
        
        return True

    def test_booking_end_before_start(self):
        '''
        Tries to create a booking that starts in the past
        '''
        b1 = Booking(
            bookable = self.bookable,
            owner = self.testuser,
            start = make_aware(datetime(2019,7,29,0,0)),
            end = make_aware(datetime(2019,7,28,23,59,59)),
            comment = "automated test"
        )
        with self.assertRaises(ValidationError):
            b1.save()
        
        return True

    def test_create_reservation(self):
        '''
        Tries to create a reservation after a booking
        '''

        b1 = Booking(
            bookable = self.bookable,
            owner = self.testuser,
            start = make_aware(datetime(2019,7,28,0,0)),
            end = make_aware(datetime(2019,7,29,23,59,59)),
            comment = "automated test"
        )
        b1.save()

        r1 = Reservation(
            bookable = self.bookable,
            owner = self.testuser,
            start = make_aware(datetime(2019,7,30,0,0)),
            comment = "automated test"
        )
        r1.save()
        
        return True
    
    def test_reservation_overlap(self):
        '''
        Tries to create two reservations, one overlapping the other
        '''
        r1 = Reservation(
            bookable = self.bookable,
            owner = self.testuser,
            start = make_aware(datetime(2019,7,30,0,0)),
            comment = "automated test"
        )
        r1.save()

        r2 = Reservation(
            bookable = self.bookable,
            owner = self.testuser,
            start = make_aware(datetime(2019,8,15,0,0)),
            comment = "automated test"
        )
        with self.assertRaises(ValidationError):
            r2.save()

        return True

    def test_reservation_booking_overlap(self):
        '''
        Tries to create a reservation that overlaps with a booking
        '''
        b1 = Booking(
            bookable = self.bookable,
            owner = self.testuser,
            start = make_aware(datetime(2019,7,28,0,0)),
            end = make_aware(datetime(2019,7,29,23,59,59)),
            comment = "automated test"
        )
        b1.save()

        r1 = Reservation(
            bookable = self.bookable,
            owner = self.testuser,
            start = make_aware(datetime(2019,7,29,0,0)),
            comment = "automated test"
        )
        with self.assertRaises(ValidationError):
            r1.save()
        
        return True
    
    def test_book_front_end(self):
        # one day booking
        self.client.force_login(self.testuser)
        response = self.client.post(f"/booking/host/{self.bookable.id}/book", {'comment':'test', 'start':now().strftime("%Y-%m-%d"), 'end':now().strftime("%Y-%m-%d")})
        
        self.assertEqual(response.url, f"/booking/host/{self.bookable.id}")

    def test_book_front_end_bad_dates_past(self):
        self.client.force_login(self.testuser)
        response = self.client.post(f"/booking/host/{self.bookable.id}/book", {'comment':'test', 'start':'2017-04-12', 'end':'2017-04-19'})
        
        self.assertFormError(response, 'form', 'start', 'Booking cannot start in the past.')
    
    def test_book_front_end_bad_dates_swapped(self):
        self.client.force_login(self.testuser)
        response = self.client.post(f"/booking/host/{self.bookable.id}/book", {'comment':'test', 'start':(now() + timedelta(days=1)).strftime("%Y-%m-%d"), 'end':now().strftime("%Y-%m-%d")})
        
        self.assertFormError(response, 'form', '__all__', 'Booking cannot end before it has started.')

    def test_book_front_end_reserved(self):
        Reservation(
            bookable=self.bookable,
            owner = self.testuser,
            comment="test",
            start = now()
        ).save()
        self.client.force_login(self.testuser)
        response = self.client.post(f"/booking/host/{self.bookable.id}/book", {'comment':'test', 'start':now().strftime("%Y-%m-%d"), 'end':now().strftime("%Y-%m-%d")})
        
        self.assertFormError(response, 'form', '__all__', 'Item is currently reserved.')
    
    def test_book_front_end_unbookable(self):
        h = Host(
            hostname="testsuspended",
            hardware = self.hh
        )
        h.save()
        b = Bookable(
            host = h,
            status="suspended"
        )
        b.save()

        self.client.force_login(self.testuser)
        response = self.client.post(f"/booking/host/{b.id}/book", {'comment':'test', 'start':now().strftime("%Y-%m-%d"), 'end':now().strftime("%Y-%m-%d")})
        
        self.assertFormError(response, 'form', '__all__', 'Host is not currently bookable.')

class BookableTests(TestCase):
    @classmethod
    def setUpTestData(self):
        ht = HostType(name="test")
        ht.save()
        hh = HostHardware(name="test", host_type=ht)
        hh.save()
        h = Host(hostname="test", hardware=hh)
        h.save()
        b = Bookable(host=h, status="active")
        b.save()
        self.bookable = b
        self.host = h

        u = User(username="test", password="test")
        u.save()
        self.testuser = u
    
    def test_get_free(self):
        self.assertEqual(self.bookable.check_booked_simple(), False)

        b1 = Booking(
            bookable = self.bookable,
            owner = self.testuser,
            start = now() - timedelta(days=1),
            end = now() + timedelta(days=1),
            comment = "automated test"
        )
        b1.save()

        self.assertNotEqual(self.bookable.check_booked_simple(), False)

        return True
    
    def test_check_reserved(self):
        self.assertEqual(self.bookable.check_reserved_simple(), False)
        r1 = Reservation(
            bookable = self.bookable,
            owner = self.testuser,
            start = now() - timedelta(days=2),
            comment = "automated test"
        )
        r1.save()
        self.assertNotEqual(self.bookable.check_reserved_simple(), False)

    
    def test_get_current_reservation(self):
        self.assertIsNone(self.bookable.get_current_reservation())
        r1 = Reservation(
            bookable = self.bookable,
            owner = self.testuser,
            start = now() - timedelta(days=2),
            comment = "automated test"
        )
        r1.save()
        self.assertEqual(self.bookable.get_current_reservation(), r1)

class EmailTests(TestCase):
    @classmethod
    def setUpTestData(self):
        ht = HostType(name="test")
        ht.save()
        hh = HostHardware(name="test", host_type=ht)
        hh.save()
        h1 = Host(hostname="test", hardware=hh)
        h1.save()
        b1 = Bookable(host=h1, status="active")
        b1.save()
        self.bookable1 = b1
        self.host1 = h1

        h2 = Host(hostname="test2", hardware=hh)
        h2.save()
        b2 = Bookable(host=h2, status="active")
        b2.save()
        self.bookable2 = b2
        self.host2 = h2

        h3 = Host(hostname="test3", hardware=hh)
        h3.save()
        b3 = Bookable(host=h3, status="active")
        b3.save()
        self.bookable3 = b3
        self.host3 = h3

        h4 = Host(hostname="test4", hardware=hh)
        h4.save()
        b4 = Bookable(host=h4, status="active")
        b4.save()
        self.bookable4 = b4
        self.host4 = h4

        h5 = Host(hostname="test5", hardware=hh)
        h5.save()
        b5 = Bookable(host=h5, status="active")
        b5.save()
        self.bookable5 = b5
        self.host5 = h5

        u = User(username="test", password="test", email="test@example.com")
        u.save()
        self.testuser = u

    def tomorrow_booking_reminder(self):
        '''
        Check the email reminders that are part of morningjobs run properly
        '''

        # create booking starting tomorrow
        bst = Booking(
            bookable = self.bookable1,
            owner = self.testuser,
            start = make_aware(datetime.fromordinal((now().date() - timedelta(days=1)).toordinal())),
            end = make_aware(datetime.fromordinal((now().date() + timedelta(days=4, hours=23, minutes=59, seconds=59)).toordinal())),
            comment = "test"
        )
        bst.save()

        # create booking starting tomorrow, reminder already sent
        bsts = Booking(
            bookable = self.bookable2,
            owner = self.testuser,
            start = make_aware(datetime.fromordinal((now().date() + timedelta(days=1)).toordinal())),
            end = make_aware(datetime.fromordinal((now().date() + timedelta(days=4, hours=23, minutes=59, seconds=59)).toordinal())),
            mail_start_reminder_sent = True,
            comment = "test"
        )
        bsts.save()

        self.client.post('/api/cron/morningjobs')

        self.assertEqual(len(mail.outbox), 1)
        self.assertContains(mail.outbox[0].subject, "booking for test2 to start")
    
    def tomorrow_ending_reminder(self):

        # create booking ending tomorrow
        bet = Booking(
            bookable = self.bookable3,
            owner = self.testuser,
            start = make_aware(datetime.fromordinal((now().date() - timedelta(days=4)).toordinal())),
            end = make_aware(datetime.fromordinal((now().date() + timedelta(days=1, hours=23, minutes=59, seconds=59)).toordinal())),
            comment = "test"
        )
        bet.save()

        self.client.post('/api/cron/morningjobs')
        self.assertEqual(len(mail.outbox), 1)
        self.assertContains(mail.outbox[0].subject, "booking for test3 is ending")
    
    def today_ended_reminder(self):
        # create booking ended today
        be2 = Booking(
            bookable = self.bookable2,
            owner = self.testuser,
            start = make_aware(datetime.fromordinal((now().date() - timedelta(days=4)).toordinal())),
            end = make_aware(datetime.fromordinal((now().date() + timedelta(hours=23, minutes=59, seconds=59)).toordinal())),
            comment = "test"
        )
        be2.save()
        self.client.post('/api/cron/morningjobs')
        self.assertEqual(len(mail.outbox), 1)
        self.assertContains(mail.outbox[0].subject, "booking for test2 has ended")

    def tomorrow_res_reminder(self):
        # create reservation starting tomorrow
        r = Reservation(
            bookable = self.bookable5,
            owner = self.testuser,
            start = make_aware(datetime.fromordinal((now().date() + timedelta(days=1)).toordinal())),
            comment = "test"
        )
        r.save()
        self.client.post('/api/cron/morningjobs')
        self.assertEqual(len(mail.outbox), 1)
        self.assertContains(mail.outbox[0].subject, "your reservation for test5 is starting")
    
    def reservation_nag(self):
        # create reservation needs nagging
        rnn = Reservation(
            bookable = self.bookable4,
            owner = self.testuser,
            start = make_aware(datetime.fromordinal((now().date() - timedelta(weeks=20)).toordinal())),
            mail_last_nag = make_aware(datetime.fromordinal((now().date() + timedelta(weeks=20)).toordinal())),
            comment = "test"
        )
        rnn.save()

        self.client.post('/api/cron/morningjobs')
        self.assertEqual(len(mail.outbox), 1)
        self.assertContains(mail.outbox[0].subject, "you have test4 reserved")

