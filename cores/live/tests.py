from django.test import TestCase
from inventory.models import Host, HostType, HostHardware, Nic, Lab, Rack, Building
from live.scanhandler import ingest
from live.models import NicScanConflict, LocationScanConflict, UnknownScanConflict, ScanConflict, ScanSession, VirtualHostsScan
from datetime import datetime
from django.contrib.auth.models import User
import json

# Create your tests here.

class LiveScanTests(TestCase):
    @classmethod
    def setUpTestData(self):
        build = Building(code="TEST")
        build.save()
        lab = Lab(name="test", building=build, network="192.168.0.0/24")
        lab.save()
        self.lab = lab
        rack = Rack(number=0, lab = lab)
        rack.save()
        lab2 = Lab(name="test2", building=build, network="10.142.180.0/24")
        lab2.save()
        self.lab2 = lab2
        rack2 = Rack(number=0, lab = lab2)
        rack2.save()
        ht = HostType(name="test")
        ht.save()
        hh = HostHardware(name="test", host_type=ht)
        hh.save()
        self.hh = hh
        h = Host(hostname="test", hardware=hh)
        h.save()
        self.host = h
        nic = Nic(
            host = h,
            mac = "a0:36:9f:af:12:34",
            ip = "10.1.1.1",
            primary = True
        )
        nic.save()
        self.nic = nic
        u = User(username="test", password="test", is_superuser=True, is_staff=True)
        u.save()
        self.testuser = u

    def test_existing_host_new_ip(self):
        '''
        Test two ingests for one host, first check IP addresses are flagged both times (nicscanconflict),
        that default rack is accepted if it's the first time we've seen the host, and that a locationscanconflict
        is created if new location doesn't match old one
        '''
        c = self.client
        c.force_login(self.testuser)

        result = c.post("/api/live/ingest", data=json.dumps({
            'agentident': 'test',
            'timestamp': str(datetime.now()),
            'results': [
                {'ip':'192.168.0.4', 'mac':'a0:36:9f:af:12:34'}
            ]
        }), content_type="application/json")
        self.assertEqual(result.json()['success'], True)
        self.assertContains(result, 'accepted 0 rack in lab as initial location')

        ss = ScanSession.objects.all()[0]

        nsc = NicScanConflict.objects.filter(nic=self.nic, scan=ss)
        self.assertEqual(nsc.count(), 1)

        lsc = LocationScanConflict.objects.filter(host=self.host, scan = ss)
        self.assertEqual(lsc.count(), 0)

        result = c.post("/api/live/ingest", data=json.dumps({
            'agentident': 'test',
            'timestamp': str(datetime.now()),
            'results': [
                {'ip':'10.142.180.2', 'mac':'a0:36:9f:af:12:34'}
            ]
        }), content_type="application/json")
        self.assertEqual(result.json()['success'], True)

        nsc = NicScanConflict.objects.filter(nic=self.nic)
        self.assertEqual(nsc.count(), 2)
        nsc = NicScanConflict.objects.filter(nic=self.nic, status="new")
        self.assertEqual(nsc.count(), 1)
        snsc = NicScanConflict.objects.filter(nic=self.nic, status="super")
        self.assertEqual(snsc.count(), 1)

        lsc = LocationScanConflict.objects.filter(host=self.host)
        self.assertEqual(lsc.count(), 1)
        self.assertEqual(lsc[0].newlab, self.lab2)
        self.assertEqual(lsc[0].nsc, nsc[0])

    def test_virtual_mac(self):
        c = self.client
        c.force_login(self.testuser)

        result = c.post("/api/live/ingest", data=json.dumps({
            'agentident': 'test',
            'timestamp': str(datetime.now()),
            'results': [
                {'ip':'192.168.0.7', 'mac':'4e:4f:41:48:00:00'}
            ]
        }), content_type="application/json")

        self.assertEqual(result.json()['success'], True)
        self.assertContains(result, 'Created new Virtual host entry')

        vhs = VirtualHostsScan.objects.all().count()
        self.assertEqual(vhs, 1)
    
    def test_unknown_mac(self):
        c = self.client
        c.force_login(self.testuser)

        result = c.post("/api/live/ingest", data=json.dumps({
            'agentident': 'test',
            'timestamp': str(datetime.now()),
            'results': [
                {'ip':'192.168.0.10', 'mac':'00:04:23:c1:a4:06'}
            ]
        }), content_type="application/json")

        self.assertEqual(result.json()['success'], True)
        self.assertContains(result, 'Created new UnknownScanConflict')
