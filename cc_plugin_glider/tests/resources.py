#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_glider/tests/resources.py
'''
from pkg_resources import resource_filename
import os
import subprocess


def get_filename(path):
    '''
    Returns the path to a valid dataset
    '''
    filename = resource_filename('cc_plugin_glider', path)
    nc_path = filename.replace('.cdl', '.nc')
    if not os.path.exists(nc_path):
        generate_dataset(filename, nc_path)
    return nc_path


def generate_dataset(cdl_path, nc_path):
    subprocess.call(['ncgen', '-o', nc_path, cdl_path])


STATIC_FILES = {
    'bad_metadata': get_filename('tests/data/gliders/bad_metadata.cdl'),
    'glider_std': get_filename('tests/data/gliders/IOOS_Glider_NetCDF_v2.0.cdl'),
    'glider_std3': get_filename('tests/data/gliders/IOOS_Glider_NetCDF_v3.0.cdl'),
    'bad_location': get_filename('tests/data/gliders/bad_location.cdl'),
    'bad_qc': get_filename('tests/data/gliders/bad_qc.cdl'),
    'no_qc': get_filename('tests/data/gliders/no_qc.cdl')
}
