# -*- coding: utf-8 -*-

import json
import urllib
import requests
import os

from bs4 import BeautifulSoup


# TODO:
# - Agregar carpeta de destino
# - Agregar única extensión o que elija por default de la lista
# - Si está ese nombre, aumentar contador y guardar
# - Agregar tiempo total
# - Agregar opción de archivo de error
# - Agregar formato para el nombre
# - Límite de imágenes


try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen


class Scraper:

    def __init__(self):
        self.session = requests.Session()
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'}
        self.url = 'https://www.google.com.ar/search?'
        self.params = {'tbm': 'isch'}
        self.output_dir = os.path.expanduser('~')
        self.allowed_extensions = ['jpg', 'jpeg', 'png', 'bmp']
        # Turn off SSL warnings
        requests.packages.urllib3.disable_warnings()

    def _make_soup(self):
        url = self.url
        for k, v in self.params.items():
            url += '%s=%s&' % (k, v)

        request = urllib.request.Request(url, headers=self.headers)
        response = urllib.request.urlopen(request)
        # Open URL and read until EOF
        html = response.read()

        return BeautifulSoup(html, "lxml")

    def download_image(self, image_url):
        extension = image_url.split('.')[-1]

        if extension not in self.allowed_extensions:
            return

        count_files = len(os.listdir(self.output_dir))

        local_filename = os.path.join(self.output_dir, '%05d.%s' % (count_files + 1, extension))
        print("Downloading '%s' as '%s" % (image_url, local_filename))

        try:
            r = self.session.get(image_url, stream=True, verify=False)
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
        except ConnectionError as e:
            print("An error has ocurred: %s" % str(e))

    def get_images(self, query, output_dir=None):

        if output_dir is not None:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.join(self.output_dir, query.replace(' ', '_'))

        if not os.path.exists(self.output_dir):
            # TODO: Ver si hay que agarrar alguna Exception
            os.makedirs(self.output_dir)

        self.params['q'] = query.replace(' ', '%20')

        soup = self._make_soup()
        topics = soup.findAll('div', {'class': 'rg_meta'})

        for topic in topics:
            self.download_image(json.loads(topic.contents[0])['ou'])


if __name__ == '__main__':
    scraper = Scraper()

    scraper.get_images('spacex wallpaper')
