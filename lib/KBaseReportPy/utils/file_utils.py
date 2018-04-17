# -*- coding: utf-8 -*-
import os

""" Utilities for validating and uploading files """


def fetch_or_upload_files(dfu, files, zip=False):
    """
    Given a list of dictionaries of files that each have either 'path' or 'shock_id'
    Return a list of file dicts that can be passed as 'html_links' or 'file_links'
    """
    out_files = []
    for file in files:
        if file['path']:
            # Having a 'path' key means we have to upload to shock
            shock = dfu.file_to_shock({
                'file_path': file['path'],
                'make_handle': 1,
                'pack': 'zip' if zip else None
            })
        elif file['shock_id']:
            # Having a 'shock_id' means it is already uploaded
            shock = dfu.own_shock_node({'shock_id': file['shock_id'], 'make_handle': 1})[0]
        print('xyz', shock)
        out_files.append(__get_file_data(shock, file))
    return out_files


def validate_file_array(name, files):
    """
    Raise an exception if any entry in `files` is:
     - not a dict
     - does not have 'path' or 'shock_id'
     - has a non-existent path
    """
    for file in files:
        print('FILE', file)
        if not isinstance(file, dict):
            raise ValueError(
                'All entries in ' + name + ' should be dictionaries: '
                + str(files)
            )
        if ('path' not in file) and ('shock_id' not in file):
            raise ValueError(
                'All entries in ' + name + ' should have either "path" or "shock_id":'
                + str(files)
            )
        if 'path' in file and (not os.path.isfile(file['path'])):
            raise ValueError(
                'File path does not exist: ' + file['path']
                + ' . Make sure the file exists in your scratch directory.'
            )


def __get_file_data(shock, file):
    """
    Return a dict that can be used in 'html_links' or 'file_links'
    :param shock: a shock dict with id, handle, etc
    :param file: a dict with shock_id, name, description, label
    """
    return {
        'handle': shock['handle']['hid'],
        'description': file.get('description', ''),
        'name': file.get('name', ''),
        'label': file.get('label', ''),
        'URL': shock['handle']['url'] + '/node/' + shock['handle']['id']
    }
