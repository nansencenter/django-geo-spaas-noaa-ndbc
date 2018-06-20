import datetime
import netCDF4
import numpy as np

from thredds_crawler.crawl import Crawl

from django.contrib.gis.geos import GEOSGeometry

from geospaas.utils import validate_uri

from noaa_ndbc.models import StandardMeteorologicalBuoy

#def populate_stdmbuoys():


def crawl(url, **options):
    if not validate_uri(url):
        raise ValueError('Invalid url: %s'%url)

    if options['year']:
        select = ['(.*%s\.nc)' %options['year']]
    elif options['filename']:
        select = ['(.*%s)' %options['filename']]
    else:
        select = None

    c = Crawl(url, select=select, skip=['.*ncml'], debug=True)
    added = 0
    for ds in c.datasets:
        url = [s.get('url') for s in ds.services if
                s.get('service').lower()=='opendap'][0]
        ndbc_stdmet, cr = StandardMeteorologicalBuoy.objects.get_or_create(url)
        if cr:
            print 'Added %s, no. %d/%d'%(url, added, len(c.datasets))
            added += 1
    return added

def get_data(utc, uri):
    """ Return data stored in a remote netCDF dataset available via OpenDAP

    TODO: this function is made for the ndbc buoys but could probably be generalized!

    Parameters
    ----------
    utc : datetime.datetime
        UTC timestamp for which data is requested
    uri : string
        The full uri of the dataset

    Returns
    -------
    out : dict
        A dictionary with the requested data at given utc

    Examples
    --------
    >>> import datetime
    >>> from noaa_ndbc.utils import get_data
    >>> uri = u'http://dods.ndbc.noaa.gov/thredds/dodsC/data/stdmet/41038/41038h2010.nc'
    >>> utc = datetime.datetime(2010, 1, 6, 2, 57, 36)
    >>> get_data(utc, uri)
    Retrieving buoy data from 2010-01-06 03:00:00
    {u'air_pressure': 1015.8,
     u'air_temperature': 3.2,
     u'average_wpd': masked,
     u'dewpt_temperature': masked,
     u'dominant_wpd': masked,
     u'gust': 11.5,
     'latitude': 34.141,
     'longitude': -77.715,
     u'mean_wave_dir': masked,
     u'sea_surface_temperature': 9.3,
     u'time': 1262746800,
     u'visibility': masked,
     u'water_level': masked,
     u'wave_height': masked,
     u'wind_dir': 306,
     u'wind_spd': 7.4}

    """
    sar_time = (utc - datetime.datetime(1970,1,1)).total_seconds()
    ds = netCDF4.Dataset(uri)
    buoy_times = ds.variables['time'][:]

    ind_min_diff = np.argmin(np.abs(sar_time - buoy_times))
    print('Retrieving buoy data from %s' %datetime.datetime.fromtimestamp(buoy_times[ind_min_diff]))

    out = {}
    out['latitude'] = ds.variables.pop('latitude')[0]
    out['longitude'] = ds.variables.pop('longitude')[0]
    for var in ds.variables:
        var_value = ds.variables[var][ind_min_diff]
        if isinstance(var_value, np.ndarray):
            var_value = var_value[0]
            if isinstance(var_value, np.ndarray):
                var_value = var_value[0]
        out[var] = var_value

    return out

