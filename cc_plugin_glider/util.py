#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_glider/util.py
'''
import csv
import numpy as np
from cc_plugin_glider.required_var_attrs import required_var_attrs
from cf_units import Unit
from operator import eq
from pkg_resources import resource_filename

_SEA_NAMES = None


def get_sea_names():
    '''
    Returns a list of NODC sea names

    source of list: https://www.nodc.noaa.gov/General/NODC-Archive/seanamelist.txt
    '''
    global _SEA_NAMES
    if _SEA_NAMES is None:
        buf = {}
        with open(resource_filename('cc_plugin_glider', 'data/seanames.csv'), 'r') as f:
            reader = csv.reader(f)
            for code, sea_name in reader:
                buf[sea_name] = code
        _SEA_NAMES = buf
    return _SEA_NAMES


def compare_dtype(dt1, dt2):
    '''
    Helper function to compare two numpy dtypes to see if they are equivalent
    aside from endianness.  Returns True if the two are equivalent, False
    otherwise.
    '''
    return eq(*(dt.kind + str(dt.itemsize) for dt in (dt1, dt2)))


def _check_dtype(dataset, var_name):
    '''
    Convenience method to check a variable datatype validity
    '''
    score = 0
    out_of = 0
    messages = []
    if var_name not in dataset.variables:
        # No need to check the attrs if the variable doesn't exist
        return (score, out_of, messages)

    var = dataset.variables[var_name]
    var_dict = required_var_attrs.get(var_name, {})
    expected_dtype = var_dict.get('dtype', None)
    if expected_dtype is not None:
        out_of += 1
        score += 1
        if not compare_dtype(var.dtype, np.dtype(expected_dtype)):
            messages.append('Variable {} is expected to have a dtype of '
                            '{}, instead has a dtype of {}'
                            ''.format(var_name, var.dtype, expected_dtype))
            score -= 1

    # check that the fill value is of the expected dtype as well
    if hasattr(var, '_FillValue') and not compare_dtype(var.dtype, var._FillValue.dtype):
        messages.append('Variable {} _FillValue dtype does not '
                        'match variable dtype'
                        ''.format(var_name, var._FillValue.dtype,
                                  var.dtype))
        out_of += 1

    return (score, out_of, messages)


def _check_variable_attrs(dataset, var_name, required_attributes=None):
    '''
    Convenience method to check a variable attributes based on the
    expected_vars dict
    '''
    score = 0
    out_of = 0
    messages = []
    if var_name not in dataset.variables:
        # No need to check the attrs if the variable doesn't exist
        return (score, out_of, messages)

    var = dataset.variables[var_name]

    # Get the expected attrs to check
    check_attrs = required_attributes or required_var_attrs.get(var_name, {})
    var_attrs = set(var.ncattrs())
    for attr in check_attrs:
        if attr == 'dtype':
            # dtype check is special, see above
            continue
        out_of += 1
        score += 1
        # Check if the attribute is present
        if attr not in var_attrs:
            messages.append('Variable {} must contain attribute: {}'
                            ''.format(var_name, attr))
            score -= 1
            continue

        # Attribute exists, let's check if there was a value we need to compare against
        if check_attrs[attr] is not None:
            if getattr(var, attr) != check_attrs[attr]:
                # No match, this may be an error, but first an exception for units
                if attr == 'units':
                    cur_unit = Unit(var.units)
                    comp_unit = Unit(check_attrs['units'])
                    if not cur_unit.is_convertible(comp_unit):
                        messages.append('Variable {} units attribute must be '
                                        'convertible to {}'.format(var_name, comp_unit))
                        score -= 1
                else:
                    messages.append('Variable {} attribute {} must be {}'.format(var_name, attr, check_attrs[attr]))
                    score -= 1
        else:
            # Final check to make sure the attribute isn't an empty string
            try:
                # try stripping whitespace, and return an error if empty
                att_strip = getattr(var, attr).strip()
                if not att_strip:
                    messages.append('Variable {} attribute {} is empty'
                                    ''.format(var_name, attr))
                    score -= 1
            except AttributeError:
                pass

    return (score, out_of, messages)

