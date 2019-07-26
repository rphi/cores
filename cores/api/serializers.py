from rest_framework import serializers
from inventory.models import Nic, Host, HdVendor, HostHardware, HostType, Rack, Building, Lab, Card, CardType
from booking.models import Bookable, Booking
from django.contrib.auth.models import User, Group

# Serializers define the API representation.
class NicSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Nic
        fields = ('__all__')

class NicIDSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Nic
        fields = ('__all__')

class HostSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Host
        exclude = ('owner',)

class HostIDSerialiser(serializers.ModelSerializer):
    bookable = serializers.IntegerField(source='bookable.id')
    class Meta:
        model = Host
        include = ('__all__')
        exclude = ('owner',)

class HdVendorSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HdVendor
        fields = ('__all__')

class HostHardwareSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HostHardware
        fields = ('__all__')

class HostTypeSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HostType
        fields = ('__all__')

class LabSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Lab
        fields = ('__all__')

class RackSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Rack
        fields = ('__all__')

class BuildingSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Building
        fields = ('__all__')

class CardSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Card
        fields = ('__all__')

class CardTypeSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CardType
        fields = ('__all__')

class HostCardSerialiser(serializers.ListField):
    def to_representation(self, value):
        return list(value.values('id', 'cardtype__name', 'details'))

class BookableSerialiser(serializers.ModelSerializer):
    hostname = serializers.ReadOnlyField(source='host.hostname')
    ip = serializers.IPAddressField(source='host.ip.ip', read_only=True)
    hardware = serializers.StringRelatedField(source='host.hardware', read_only=True)
    cards = HostCardSerialiser(source='host.cards.values', read_only=True)
    rack = serializers.StringRelatedField(source='host.rack', read_only=True)
    booked = serializers.ReadOnlyField(source='check_booked_simple')
    reserved = serializers.ReadOnlyField(source='check_reserved_simple')
    class Meta:
        model = Bookable
        fields = ('__all__')

class BookingSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('__all__')

class UserSerialiser(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'last_login', 'date_joined', 'user_permissions')

class GroupSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('__all__')
