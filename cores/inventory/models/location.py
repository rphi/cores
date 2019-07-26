from django.db import models
from netfields import CidrAddressField, NetManager

class Building(models.Model):
    code = models.CharField(max_length=8)
    comment = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return self.code

class Lab(models.Model):
    name = models.CharField(max_length=30)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='labs')
    comment = models.CharField(max_length=30, null=True, blank=True)
    network = CidrAddressField(null=True, blank=True)
    objects = NetManager()

    def __str__(self):
        return self.building.code + '/' + self.name

class Rack(models.Model):
    number = models.PositiveIntegerField()
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='racks')
    comment = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return str(self.number) + ' in ' + self.lab.building.code + '/' + self.lab.name
