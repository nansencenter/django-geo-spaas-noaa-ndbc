from django.core.management.base import BaseCommand, CommandError

from noaa_ndbc.utils import crawl

class Command(BaseCommand):
    args = '<url> <select>'
    help = '''
        Add buoy metadata to archive. 
        
        Args:
            <url>: the url to the thredds server
            <select>: You can select datasets based on their THREDDS ID using
            the 'select' parameter.
            
        Example: 
            (1) Find all NOAA NDBC standard meteorological buoys in 2009

            url = http://dods.ndbc.noaa.gov/thredds/catalog/data/stdmet/catalog.xml
            select = 2009

            (2) Find a specific file

            url = http://dods.ndbc.noaa.gov/thredds/catalog/data/stdmet/catalog.xml
            select = 0y2w3h2012.nc
        '''
    def add_arguments(self, parser):
        parser.add_argument('url', nargs='*', type=str)
        parser.add_argument('--year',
                            action='store',
                            default='',
                            help='''Year of coverage''')
        parser.add_argument('--filename',
                            action='store',
                            default='',
                            help='''Filename of a specific dataset''')

    def handle(self, *args, **options):
        if not len(options['url'])==1:
            raise IOError('Please provide a url to the data')
        url = options.pop('url')[0]
        added = crawl(url, **options)
        self.stdout.write(
            'Successfully added metadata of %s stdmet buouy datasets' %added)
