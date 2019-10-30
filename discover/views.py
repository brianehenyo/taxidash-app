from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from geopy import units, distance
from django.urls import reverse
from django.utils import timezone
from django.template import loader

from .models import Trip, Meetup, Passenger, TaxiCompany
from django.db.models import Count
from django.http import JsonResponse
from datetime import datetime, timedelta

from django.template import RequestContext

MAX_PASSENGERS = 4
ALLOWABLE_DIST = 0.4

def index(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')

    try:
        request.session['joined_trip']
    except KeyError:
        request.session['joined_trip'] = -1
        request.session['prevPage'] = 'index'
        request.session['host_ip'] = ip
        return render(request, 'discover/discover.html')
    else:
        if request.session['joined_trip'] != -1:
            context = {'error_message': "You cannot join another trip. You will be redirected...",
                       'redirect': request.session['joined_trip']}
            return render(request, 'discover/discover.html', context)
        else:
            request.session['prevPage'] = 'index'
            context = {'ip': ip}
            request.session['host_ip'] = ip

            return render(request, 'discover/discover.html', context)


def refreshtrips(request):
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')

    request.session['latitude'] = latitude
    request.session['longitude'] = longitude

    lat = float(latitude)
    long = float(longitude)
    distance_range = float(ALLOWABLE_DIST)

    rough_distance = units.degrees(arcminutes=units.nautical(kilometers=distance_range)) * 2

    # all_trips = Trip.objects.filter(date__date=timezone.now() + timedelta(hours=9), status='ACT', meetup_pt__latitude__range=(lat - rough_distance, lat + rough_distance), meetup_pt__longitude__range=(long - rough_distance, long + rough_distance)).annotate(avail_passengers=MAX_PASSENGERS - Count('passenger')).filter(avail_passengers__lte=4, avail_passengers__gt=0).order_by('avail_passengers')

    all_trips = Trip.objects.filter(date__date=timezone.now() + timedelta(hours=9), status='ACT', latitude__range=(lat - rough_distance, lat + rough_distance), longitude__range=(long - rough_distance, long + rough_distance)).annotate(avail_passengers=MAX_PASSENGERS - Count('passenger')).filter(avail_passengers__lte=4, avail_passengers__gt=0).order_by('avail_passengers')

    # all_trips = Trip.objects.filter(status='ACT', latitude__range=(lat - rough_distance, lat + rough_distance), longitude__range=(long - rough_distance, long + rough_distance)).annotate(avail_passengers=MAX_PASSENGERS - Count('passenger')).filter(avail_passengers__lte=4, avail_passengers__gt=0).order_by('avail_passengers')

    nearby = []
    for trip in all_trips:
        if trip.latitude and trip.longitude:
            exact_distance = distance.distance(
                (lat, long),
                (trip.latitude, trip.longitude)
            ).kilometers

            if exact_distance <= distance_range:
                trip.distance = exact_distance
                nearby.append(trip)

    sorted(nearby, key=lambda m: m.distance)

    closest = []
    if len(nearby) > 0:
        closest.append({"id": nearby[0].id, "latitude": nearby[0].latitude, "longitude": nearby[0].longitude})

    # trip_cards = loader.render_to_string('discover/tripcards.html', {'trips': nearby})
    # output_data = {'trip_cards': trip_cards}
    output_data = {'trips': closest}
    return JsonResponse(output_data)


def taxiList(request):
    try:
        request.session['prevPage']
        request.session['joined_trip']
    except:
        request.session['prevPage'] = 'index'
        request.session['joined_trip'] = -1

    taxi_companies = TaxiCompany.objects.all()

    context = {'trip_id': request.session['joined_trip'],
               'referer': request.session['prevPage'],
               'companies': taxi_companies}
    return render(request, 'discover/taxilist.html', context)


def back(request):
    referer = request.session['prevPage']
    trip_id = request.session['joined_trip']

    if "detail" in referer:
        return HttpResponseRedirect(reverse('discover:detail', args=(trip_id,)))
    else:
        return HttpResponseRedirect(reverse('discover:index'))


def enroute(request):
    trip_id = request.session['joined_trip']

    try:
        trip = Trip.objects.get(pk=trip_id)
    except (KeyError, Trip.DoesNotExist):
        context = {'error_message': "Your trip has already started."}
    else:
        trip.status = Trip.ENROUTE
        trip.save()
        passengers = Passenger.objects.filter(trip=trip)

        request.session['joined_trip'] = -1
        request.session['passenger'] = ""
        request.session['passengerID'] = -1

        context = {'trip': trip,
                   'passengers': passengers}

    return render(request, 'discover/enroute.html', context)


def detail(request, trip_id):
    try:
        trip = Trip.objects.get(pk=trip_id)
        # trip = Trip.objects.get(pk=request.session['joined_trip'])
    except Trip.DoesNotExist:
        context = {'error_message': "This trip does not exist :("}
        return render(request, 'discover/trip.html', context)
    else:
        try:
            request.session['joined_trip']
        except KeyError:
            context = {'error_message': "You have not joined any trip. You will be redirected...",
                       'redirect': -1}
            return render(request, 'discover/trip.html', context)
        else:
            if int(trip_id) != int(request.session['joined_trip']):
                context = {'error_message': "You did not join this trip. You will be redirected...",
                           'redirect': request.session['joined_trip']}
            else:
                if trip.status == 'ACT':
                    passengers = Passenger.objects.filter(trip=trip)
                    request.session['prevPage'] = 'detail'
                    context = {'trip': trip,
                               'passengers': passengers}
                else:
                    context = {'error_message': "This trip has started already. You will be redirected...",
                       'redirect': -1}
                    request.session['joined_trip'] = -1
                    request.session['passenger'] = ""
                    request.session['passengerID'] = -1
            return render(request, 'discover/trip.html', context)


def join(request):
    trip_id = request.POST.get('trip_id')
    passenger = request.POST.get('organizer')
    passenger = passenger.strip(' ')

    if len(passenger) == 0:
        context = {'error_message': "You did not enter a name when you tried to join a trip. Please type your name or nickname next time :)"}
        return render(request, 'discover/discover.html', context)
    else:
        request.session['passenger'] = passenger
        latitude = request.session['latitude']
        longitude = request.session['longitude']

        lat = float(latitude)
        long = float(longitude)

        ip = request.session['host_ip']

        join_trip = Trip.objects.get(pk=trip_id)
        passengers = Passenger.objects.filter(trip=join_trip)
        if passengers.count() < 4 and join_trip.status == 'ACT':
            new_passenger = Passenger(trip=join_trip, name=passenger, ip=ip, latitude=lat, longitude=long)
            new_passenger.save()
            request.session['joined_trip'] = trip_id
            request.session['passengerID'] = new_passenger.id
            return HttpResponseRedirect(reverse('discover:detail', args=(trip_id,)))
        else:
            context = {
                'error_message': "I'm sorry but you can't join that trip anymore. Please select another one below or organize a new trip."}
            return render(request, 'discover/discover.html', context)


def leave(request):
    trip_id = request.session['joined_trip']
    pass_ID = request.session['passengerID']

    trip = Trip.objects.get(pk=trip_id)
    passenger = Passenger.objects.get(pk=pass_ID)
    passenger.delete()

    passengers = Passenger.objects.filter(trip=trip)
    if passengers.count() == 0:
        trip.status = Trip.CANCELLED
        trip.save()

    request.session['joined_trip'] = -1
    request.session['passenger'] = ""
    request.session['passengerID'] = -1

    return HttpResponseRedirect(reverse('discover:index'))


def organize(request):
    if request.POST.get('latitude') is not None and request.POST.get('longitude') is not None:
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        request.session['latitude'] = latitude
        request.session['longitude'] = longitude

        lat = float(latitude)
        long = float(longitude)
        distance_range = float(ALLOWABLE_DIST)

        rough_distance = units.degrees(arcminutes=units.nautical(kilometers=distance_range)) * 2

        all_meetup_pts = Meetup.objects.filter(latitude__range=(lat - rough_distance, lat + rough_distance),
                                               longitude__range=(long - rough_distance, long + rough_distance))

        nearby = []
        for meetup_pt in all_meetup_pts:
            if meetup_pt.latitude and meetup_pt.longitude:
                exact_distance = distance.distance(
                    (lat, long),
                    (meetup_pt.latitude, meetup_pt.longitude)
                ).kilometers

                if exact_distance <= distance_range:
                    meetup_pt.distance = exact_distance
                    nearby.append(meetup_pt)

        sorted(nearby, key=lambda m: m.distance)

        context = {'nearby_meetups': nearby}
        return render(request, 'discover/organize.html', context)
    else:
        return HttpResponseRedirect(reverse('discover:index'))

def createTrip(request):
    organizer = request.POST.get('organizer')
    email = request.POST.get('email')
    # selected_meetup = request.POST.get('choice')
    organizer = organizer.strip(' ')
    email = email.strip(' ')

    latitude = request.session['latitude']
    longitude = request.session['longitude']

    lat = float(latitude)
    long = float(longitude)

    new_trip = Trip(organizer=organizer, latitude=lat, longitude=long, date=timezone.now() + timedelta(hours=9))
    new_trip.save()

    ip = request.session['host_ip']
    new_passenger = Passenger(trip=new_trip, name=organizer, email=email, ip=ip, latitude=lat, longitude=long)
    new_passenger.save()

    request.session['joined_trip'] = new_trip.id
    request.session['passenger'] = organizer
    request.session['passengerID'] = new_passenger.id

    return HttpResponseRedirect(reverse('discover:detail', args=(new_trip.id,)))

    # if len(organizer) == 0 | len(email) == 0:
        # distance_range = float(ALLOWABLE_DIST)

        # rough_distance = units.degrees(arcminutes=units.nautical(kilometers=distance_range)) * 2

        # all_meetup_pts = Meetup.objects.filter(latitude__range=(lat - rough_distance, lat + rough_distance),
        #                                        longitude__range=(long - rough_distance, long + rough_distance))

        # nearby = []
        # for meetup_pt in all_meetup_pts:
        #     if meetup_pt.latitude and meetup_pt.longitude:
        #         exact_distance = distance.distance(
        #             (lat, long),
        #             (meetup_pt.latitude, meetup_pt.longitude)
        #         ).kilometers

        #         if exact_distance <= distance_range:
        #             meetup_pt.distance = exact_distance
        #             nearby.append(meetup_pt)

        # all_trips = Trip.objects.filter(date__date=timezone.now() + timedelta(hours=9), status='ACT', latitude__range=(lat - rough_distance, lat + rough_distance), longitude__range=(long - rough_distance, long + rough_distance)).annotate(avail_passengers=MAX_PASSENGERS - Count('passenger')).filter(avail_passengers__lte=4, avail_passengers__gt=0).order_by('avail_passengers')

        # nearby = []
        # for trip in all_trips:
        #     if trip.latitude and trip.longitude:
        #         exact_distance = distance.distance(
        #             (lat, long),
        #             (trip.latitude, trip.longitude)
        #         ).kilometers

        #         if exact_distance <= distance_range:
        #             trip.distance = exact_distance
        #             nearby.append(trip)

        # sorted(nearby, key=lambda m: m.distance)

        # context = {'trips': nearby,
        #            'error_message': "You did not enter a handle name and/or email. Please type your name or nickname, and an email."}

        # context = {'error_message': "You did not enter a handle name and/or email. Please type your name or nickname, and an email."}

        # return render(request, 'discover/organize.html', context)
        # return render(request, 'discover/discover.html', context)
    # else:
        # new_meetup = get_object_or_404(Meetup, pk=selected_meetup)
