from rest_framework import viewsets
from booking.models import Bookable, Booking
from inventory.models import Nic, Host, HdVendor, HostHardware, HostType, Rack, Building, Lab, Card, CardType
from django.contrib.auth.models import User, Group
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.schemas import ManualSchema, AutoSchema
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly
from coreapi import Field
import coreschema

# ViewSets define the view behavior.
class NicViewSet(viewsets.ModelViewSet):
    queryset = Nic.objects.all()
    serializer_class = NicSerialiser

class NicIDViewSet(viewsets.ModelViewSet):
    '''
    Same as Nic list, but this addresses foreign keys with ID
    as opposed to a URL.
    '''
    queryset = Nic.objects.all()
    serializer_class = NicIDSerialiser

class HostViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostSerialiser

class HostIDViewSet(viewsets.ModelViewSet):
    '''
    Same as Host list, but this addresses foreign keys with ID
    as opposed to a URL.
    '''
    serializer_class = HostIDSerialiser
    filter_backends = (DjangoFilterBackend,)
    queryset = Host.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Host.objects.all()
        hostname = self.request.query_params.get('hostname', None)
        if hostname is not None:
            queryset = queryset.filter(hostname__iexact=hostname)
        mac = self.request.query_params.get('mac', None)
        if mac is not None:
            queryset = queryset.filter(nics__mac=mac)
        return queryset

class HdVendorViewSet(viewsets.ModelViewSet):
    queryset = HdVendor.objects.all()
    serializer_class = HdVendorSerialiser

class HostHardwareViewSet(viewsets.ModelViewSet):
    queryset = HostHardware.objects.all()
    serializer_class = HostHardwareSerialiser
    
class HostTypeViewSet(viewsets.ModelViewSet):
    queryset = HostType.objects.all()
    serializer_class = HostTypeSerialiser

class LabViewSet(viewsets.ModelViewSet):
    queryset = Lab.objects.all()
    serializer_class = LabSerialiser

class RackViewSet(viewsets.ModelViewSet):
    queryset = Rack.objects.all()
    serializer_class = RackSerialiser

class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerialiser

class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerialiser

class CardTypeViewSet(viewsets.ModelViewSet):
    queryset = CardType.objects.all()
    serializer_class = CardTypeSerialiser

class BookableViewSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method=='GET' and 'id' not in path:
            extra_fields = [
                Field('active', required=False, location='query', schema=coreschema.String(description='Boolean, if set will only show bookables marked as "Active"')),
                Field('mine', required=False, location='query', schema=coreschema.String(description='Boolean, if set will only show bookables for hosts with the current user as the owner')),
                Field('mygroup', required=False, location='query', schema=coreschema.String(description='Boolean, if set will only show bookables for hosts assigned to one of the user\'s groups')),
                Field('lab', required=False, location='query', schema=coreschema.String(description='Filter only those in lab ID')),
                Field('building', required=False, location='query', schema=coreschema.String(description='Filter only those in building ID')),
                Field('hw', required=False, location='query', schema=coreschema.String(description='Filter only those with HostHardware of ID')),
                Field('htype', required=False, location='query', schema=coreschema.String(description='Filter only those in HostType of ID')),
                Field('lab', required=False, location='query', schema=coreschema.String(description='Filter only those in lab ID')),
                Field('nores', required=False, location='query', schema=coreschema.String(description='Boolean, if set will exclude bookables that are reserved')),
                Field('free', required=False, location='query', schema=coreschema.String(description='Boolean, if set will only show bookables that are free to book now')),
            ]
        
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields

class BookableViewSet(viewsets.ModelViewSet):
    queryset = Bookable.objects.all()
    serializer_class = BookableSerialiser
    filter_backends = (OrderingFilter,)
    ordering_fields = ('host__hostname',)
    ordering = ('host__hostname', 'host__ip')
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]

    schema = BookableViewSchema()

    def get_queryset(self):
        queryset = Bookable.objects.all()

        active = self.request.query_params.get('active', None)
        if active is not None:
            if active in ['True', 'true', '1']:
                queryset = queryset.filter(status='active')
        
        mine = self.request.query_params.get('mine', None)
        if mine is not None and self.request.user.is_authenticated:
            if mine in ['True', 'true', '1']:
                queryset = queryset.select_related('host').filter(host__owner=self.request.user)

        mygroup = self.request.query_params.get('mygroup', None)
        if mygroup is not None:
            if mygroup in ['True', 'true', '1']:
                queryset = queryset.select_related('host').filter(host__group__in=self.request.user.groups.all())
        
        lab = self.request.query_params.get('lab', None)
        if lab is not None:
            queryset = queryset.select_related('host__rack').filter(host__rack__lab__in=lab.split(','))
        
        building = self.request.query_params.get('building', None)
        if building is not None:
            queryset = queryset.select_related('host__rack__lab').filter(host__rack__lab__building__in=building.split(','))
        
        hw = self.request.query_params.get('hw', None)
        if hw is not None:
            queryset = queryset.select_related('host').filter(host__hardware__in=hw.split(','))
        
        htype = self.request.query_params.get('htype', None)
        if htype is not None:
            queryset = queryset.select_related('host__hardware').filter(host__hardware__host_type__in=htype.split(','))
        
        nores = self.request.query_params.get('nores', None)
        if nores is not None:
            if nores in ['True', 'true', '1']:
                ids = [b.id for b in queryset if not b.check_reserved()]
                queryset = Bookable.objects.all().filter(id__in=ids)

        free = self.request.query_params.get('free', None)
        if free is not None:
            if free in ['True', 'true', '1']:
                ids = [b.id for b in queryset if not b.check_free()]
                queryset = Bookable.objects.all().filter(id__in=ids)
        
        ipsort = self.request.query_params.get('ipsort', None)
        if ipsort is not None:
            if ipsort in ['True', 'true', '1']:
                self.ordering = ('host__ip')

        return queryset

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerialiser

    def get_queryset(self):
        queryset = Booking.objects.all()
        owner = self.request.query_params.get('owner', None)
        if owner is not None:
            queryset = queryset.filter(owner=owner)
        bookable = self.request.query_params.get('bookable', None)
        if bookable is not None:
            queryset = queryset.filter(bookable=bookable)
        import_id = self.request.query_params.get('import_id', None)
        if import_id is not None:
            queryset = queryset.filter(import_id=import_id)
        return queryset

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerialiser
    permission_classes = [DjangoModelPermissions]

    def get_queryset(self):
        queryset = User.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(username__iexact=username)
        email = self.request.query_params.get('email', None)
        if email is not None:
            queryset = queryset.filter(email__iexact=email)
        return queryset

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerialiser
    permission_classes = [DjangoModelPermissions]

    def get_queryset(self):
        queryset = Group.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__iexact=name)
        return queryset
