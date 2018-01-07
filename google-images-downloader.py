# -*- coding: utf-8 -*-

import json
import logging
import requests
import optparse
import os
import time

from bs4 import BeautifulSoup
from time import localtime, strftime


class GoogleImagesScraper:

    def __init__(self,
                 exts=['jpg', 'jpeg', 'png', 'bmp'],
                 output_dir=os.path.expanduser('~'),
                 prefix='',
                 suffix='',
                 limit=100,
                 logger=False):
        # We will make (maybe) several request to the same host, so reusing the same TCP connection
        # result in a significant performance increase
        self.session = requests.Session()
        self.session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'}
        )

        # Google Image search default parameters
        self.url = 'https://www.google.com.ar/search?'
        self.params = {'tbm': 'isch'}
        self.allowed_exts = exts

        # By default, save images and log file in a folder inside home directory
        self.output_dir = output_dir

        # Default prefix and suffix for output file names
        self.prefix = prefix if prefix == '' else prefix + '-'
        self.suffix = suffix if suffix == '' else '-' + suffix

        # Downloads limit
        self.limit = int(limit)

        # Number of files in output_dir
        self.counter = 0

        # Set logger
        self._set_logger(logger)

        # Turn off SSL warnings
        requests.packages.urllib3.disable_warnings()

    def _set_logger(self, has_logger):
        if has_logger:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s [%(levelname)-8s] %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=os.path.join(self.output_dir, strftime('%Y%m%d_%H%M%S', localtime()) + '.log'),
                filemode='a')
            self.logger = logging.getLogger('logger')
        else:
            self.logger = logging.getLogger('None')

    def _make_soup(self):
        self.logger.debug('Making URL')
        # Create the URL
        url = self.url
        for k, v in self.params.items():
            url += '%s=%s&' % (k, v)

        self.logger.debug('Getting URL content')
        # Get the URL content and convert to a tree
        request = self.session.get(url)
        html = request.content

        self.logger.debug('Returning BeautifulSoup tree')
        return BeautifulSoup(html, "lxml")

    def _download_image(self, image_url):
        self.logger.debug('Getting image URL')
        # Get image extension
        extension = image_url.split('.')[-1]

        self.logger.debug('Checking if image extension is allowed')
        # If image extension is not in the allowed extensions, return
        if extension.lower() not in self.allowed_exts:
            self.logger.debug('Image extension not allowed. Returning...')
            return

        self.logger.debug('Setting image filename')
        # Set local filename and update counter attribute
        local_filename = os.path.join(self.output_dir, '%s%04d%s.%s' % (self.prefix, self.counter + 1, self.suffix, extension))
        self.counter += 1

        self.logger.info('"%s" image downloaded from "%s"' % (local_filename, image_url))
        # Get image bytes and save them in 'local_filename'
        try:
            r = self.session.get(image_url, stream=True, verify=False)
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
        except ConnectionError as e:
            self.logger.error('An error has ocurred: %s' % str(e))

    def download_images(self, query, output_dir=None):
        start = time.time()
        images_down = 0
        self.logger.debug('Setting output directory')
        # If output path is given, set attribute output_dir
        # If not, save images in home directory + query string with underscores
        if output_dir is not None:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.join(self.output_dir, query.replace(' ', '_'))

        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
            except OSError as e:
                self.logger.info('The directory "%s" already exists.' % self.output_dir)
            else:
                self.logger.info('"%s" directory created' % self.output_dir)

        # The counter attribute, used to name image files
        self.counter = len(os.listdir(self.output_dir))

        # Set query param to use in URL
        self.params['q'] = query.replace(' ', '%20')

        # Make soup and find all image divs
        soup = self._make_soup()
        image_divs = soup.findAll('div', {'class': 'rg_meta'})

        self.logger.debug('Traversing image divs to find image URLs')
        # For each div, create a JSON object and get 'ou' value, which is the image URL and download it
        for div in image_divs:
            if images_down < self.limit:
                self._download_image(json.loads(div.contents[0])['ou'])
                images_down += 1
            else:
                elapsed_time = time.time() - start
                self.logger.debug('Image limit exceeded. Return images downloaded')
                self.logger.info('%d images downloaded in %.2f seconds' % (images_down, elapsed_time))
                return images_down, elapsed_time

        elapsed_time = time.time() - start
        self.logger.info('%d images downloaded in %.2f seconds' % (images_down, elapsed_time))
        return images_down, elapsed_time


if __name__ == '__main__':
    # Create OptionParser object and set options
    parser = optparse.OptionParser(description='Scrap Google Images pages and download images from given query.')

    parser.add_option('-q', '--query', dest='query',
                      help='keywords for search images in Google Images, separated by commas', default='')
    parser.add_option('-l', '--limit', dest='limit',
                      help='max number of images to download (default: 100)', default='100')
    parser.add_option('-o', '--output', dest='output_dir',
                      help='directory where downloaded images will be stored', default=os.path.expanduser('~'))
    parser.add_option('-e', '--extensions', dest='exts',
                      help='allowed extensions to download, separated by commas', default='jpg,jpeg,png,bmp')
    parser.add_option('-L', '--logger', dest='logger', action='store_true',
                      help='enable logging', default=False)
    parser.add_option('-p', '--prefix', dest='prefix',
                      help='set prefix for image filenames', default='')
    parser.add_option('-s', '--suffix', dest='suffix',
                      help='set suffix for image filenames', default='')

    opts, args = parser.parse_args()

    # Store the command-line arguments in dictionary
    kwargs = vars(opts)

    # Format 'query' argument and delete it from dictionary (dictionary will be used to create the scraper object)
    query = kwargs['query'].replace(',', ' ')
    del kwargs['query']

    # Format the allowed extensions
    kwargs['exts'] = [x for x in kwargs['exts'].split(',')]

    # Create scraper object
    scraper = GoogleImagesScraper(**kwargs)

    # Download images
    count, elapsed = scraper.download_images(query)
    print('%d images downloaded in %.2f seconds' % (count, elapsed))
