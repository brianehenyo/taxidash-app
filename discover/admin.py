from django.contrib import admin

from .models import Trip, Passenger, Meetup, TaxiCompany

class MeetupAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'location')

class TripAdmin(admin.ModelAdmin):
    list_display = ('organizer', 'meetup_pt', 'date', 'status')

class PassengerAdmin(admin.ModelAdmin):
    list_display = ('name', 'trip', 'ip', 'latitude', 'longitude')

class TaxiCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact')

admin.site.register(Trip, TripAdmin)
admin.site.register(Meetup, MeetupAdmin)
admin.site.register(Passenger, PassengerAdmin)
admin.site.register(TaxiCompany, TaxiCompanyAdmin)
