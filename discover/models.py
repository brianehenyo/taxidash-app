from django.db import models
from datetime import datetime

class Meetup(models.Model):
    location = models.TextField('Address', blank=True)
    latitude = models.FloatField('Latitude', blank=True, null=True)
    longitude = models.FloatField('Longitude', blank=True, null=True)
    name = models.TextField('Name', blank=True)

    def __str__(self):
        return self.name

class Trip(models.Model):
    ACTIVE = 'ACT'
    CANCELLED = 'CAN'
    ENROUTE = 'ENR'
    STATUS_CHOICE = (
        (ACTIVE, "Active"),
        (CANCELLED, "Cancelled"),
        (ENROUTE, "En Route")
    )
    # meetup_pt = models.ForeignKey(Meetup, on_delete=models.CASCADE)
    organizer = models.CharField(max_length=200)
    latitude = models.FloatField('Latitude', blank=True, null=True, default=41.8415321)
    longitude = models.FloatField('Longitude', blank=True, null=True, default=140.7668693)
    date = models.DateTimeField('date organized', default=datetime.now)
    status = models.CharField(max_length=3, choices=STATUS_CHOICE, default=ACTIVE)

    def __str__(self):
        return self.organizer

class Passenger(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, default='default@sumilab.org')
    ip = models.CharField('IP', max_length=15, default='127.0.0.1')
    latitude = models.FloatField('Latitude', blank=True, null=True, default=41.8415321)
    longitude = models.FloatField('Longitude', blank=True, null=True, default=140.7668693)

    def __str__(self):
        return self.name

class TaxiCompany(models.Model):
    name = models.CharField(max_length=200)
    contact = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Log(models.Model):
    date = models.DateTimeField('date', default=datetime.now)
    activity = models.CharField(max_length=2000)

    def __str__(self):
        return self.activity

class Chat(models.Model):
    date = models.DateTimeField('date', default=datetime.now)
    message = models.CharField(max_length=6000)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, default='default@sumilab.org')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)

    def __str__(self):
        return self.message