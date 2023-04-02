"""
It downloads the suitable file depending on Numpy's version 
Written according to Alberto Lorenzo Márquez's advice:
http://stackoverflow.com/questions/21855775/numpy-i-is-missing-what-is-the-recommended-way-to-install-it#21857995
"""

import re
import requests
import numpy

print('Going to download numpy.i from the Internet')

np_version = re.compile(r'(?P<MAJOR>[0-9]+)\.'
                        '(?P<MINOR>[0-9]+)') \
                        .search(numpy.__version__)
np_version_string = np_version.group()
np_version_info = {key: int(value)
                   for key, value in list(np_version.groupdict().items())}

np_file_name = 'numpy.i'
np_file_url = 'https://raw.githubusercontent.com/numpy/numpy/maintenance/' + \
              np_version_string + '.x/tools/swig/' + np_file_name
if(np_version_info['MAJOR'] == 1 and np_version_info['MINOR'] < 9):
    np_file_url = np_file_url.replace('tools', 'doc')

chunk_size = 8196
with open('wwol/engine/c_part/' + np_file_name, 'wb') as file:
    for chunk in requests.get(np_file_url,
                              stream=True).iter_content(chunk_size):
        file.write(chunk)
print('SUCCESS')


