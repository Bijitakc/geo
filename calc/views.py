from django.shortcuts import render,get_object_or_404
from .models import Measurement
from .utils import get_geo,get_center_coord,get_zoom,get_ip_address
import folium
from geopy.distance import geodesic
from .forms import MeasurementModelForm
from geopy.geocoders import Nominatim
# Create your views here.

def index(request):
    return render(request,'calc/index.html')

def calculate_distance_view(request):
    #initial values
    distance=None
    destination=None
    form=MeasurementModelForm(request.POST or None)
    geolocator=Nominatim(user_agent='calc')

    #for now static ip is used
    ip_=get_ip_address(request)
    ip='72.14.207.99'
    country,city,lat,lon=get_geo(ip)
    location=geolocator.geocode(city)
    # print('###',location)

    l_lat=lat
    l_lon=lon
    pointA=(l_lat,l_lon)

    #initial follium map
    m=folium.Map(width=800,height=500,location=get_center_coord(l_lat,l_lon),zoom_start=8)
    #location marker
    folium.Marker([l_lat,l_lon],tooltip='Click here for more',popup=city['city']
    , icon=folium.Icon(color="red")).add_to(m)

    if form.is_valid():
        instance=form.save(commit=False)
        destination_=form.cleaned_data.get('destination')
        destination=geolocator.geocode(destination_)
        # print(destination)

        d_lat=destination.longitude
        d_lon=destination.latitude
        pointB=(d_lat,d_lon)

        distance=round(geodesic(pointA,pointB).km,2)

        #folium map modification
        m=folium.Map(width=800,height=500,location=get_center_coord(d_lat,d_lon),zoom_start= get_zoom(distance))
        #  location marker
        folium.Marker([l_lat,l_lon],tooltip='Click here for more',popup=city['city']
        , icon=folium.Icon(color="red")).add_to(m)
        #  destination marker
        folium.Marker([d_lat,d_lon],tooltip='Click here for more',popup=destination
        , icon=folium.Icon(color="blue",icon='cloud')).add_to(m)

        #drawing a lone from location to destination
        line=folium.PolyLine(locations=[pointA,pointB],weight=1.5,color='blue')
        m.add_child(line)

        instance.location=location
        instance.distance=distance
        instance.save()

    # If you want to HTML-display multiple objects, you'll have to explicitly wrap them with a wrapper class that has its own _repr_html_ 
    m=m._repr_html_()
    context={
            'distance':distance,
            'form':form,
            'map':m,
            'destination':destination
        }
    return render(request,'calc/main.html',context)