# Google Images Downloader

**google-images-downloader** is a project for easily download tons of images from Google Images with a given query.

Are you mastering your computer vision skills (like me)? Do you need a lot of images to test your models but you don't want to download them by hand? **google-images-downloader** is here to help you!


## Installation

Just clone the repository, install the requirements (listed in the `requirements.txt` file) in your virtual environment and start to use it.

```
git clone https://github.com/fferrin/google-images-downloader.git
mkvirtualenv -p python3 google-images-venv3
workon google-images-venv3
cd google-images-downloader/
pip install -r requirements.txt
```

## Requirements

* `requests` and `urllib3`: To make the requests to Google Images.
* `lxml`: HTML parser.
* `beautifulsoup4`: Library for pulling data out of the HTML files and allow ways of navigating, searching and modify the parse tree.


## Usage

You can start using **google-images-downloader** just by passing the search that you want, separated by commas. For example:

```
python3 google-images-downloader.py nyan,cat
```

This command will download the first 100 results for *nyan cat* and will store them in `$HOME/nyan_cat/` directory.

It also has another options, like:
* ```-l, --limit```: Set max number of images to download (default: 100).
* ```-o, --output```: Set directory where downloaded images will be stored (default: Home directory + query with underscores).
* ```-e, --extensions```: Set of allowed extensions, separated by commas (default: jpg, jpeg, png, bmp).
* ```-L, --logger```: Enable logging, stored in downloaded images directory (default: False).
* ```-p, --prefix```: Set prefix for image filenames.
* ```-p, --prefix```: Set suffix for image filenames.


### TODO
* Option to search by page results (urgent!).
* Compress files and send by email (?).
* Compress files and upload to the available cloud storage services (?).
* Suggestions?


### License

**google-images-downloader** is [MIT licensed](./LICENSE).
