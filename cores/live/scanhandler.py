from inventory.models import Host, Lab, Nic
from .models import ScanConflict, ScanSession, LocationScanConflict, NicScanConflict, UnknownScanConflict, VirtualHostsScan, OfflineHostWarning, IgnoredMac
from ipaddress import ip_address, ip_network
from django.utils import timezone, dateparse
from django.db.models import Value, CharField, F, ExpressionWrapper, Q
from netaddr import EUI
from netaddr.core import AddrFormatError
import json

def ingest(scan):
    if not ('results' in scan and 'agentident' in scan):
        return {
                'error': 'Invalid request format',
                'detail': 'Need results, agentident'
            }
    if 'timestamp' in scan:
        timestamp = timezone.make_aware(dateparse.parse_datetime(scan['timestamp']))
        
        existingscan = ScanSession.objects.filter(agent_identifier=scan['agentident'], timestamp=timestamp)
        if existingscan.exists():
            return {
                'error': 'Duplicate scan data recieved.',
                'detail': f'ScanSession from host {scan["agentident"]} with timestamp {scan["timestamp"]} already exists. Ignoring data.'
            }
        
    else:
        timestamp = timezone.now()

    ss = ScanSession(
        agent_identifier = scan['agentident'],
        timestamp =  timestamp,
        raw_data = json.dumps(scan['results'])
    )
    ss.save()

    response = ss.process_ingest()

    return response
