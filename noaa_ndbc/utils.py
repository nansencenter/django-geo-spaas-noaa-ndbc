import netCDF4
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
