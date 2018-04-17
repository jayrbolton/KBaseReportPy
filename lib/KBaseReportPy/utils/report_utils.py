# -*- coding: utf-8 -*-
from file_utils import validate_file_array, fetch_or_upload_files
from uuid import uuid4

""" Utilities for creating reports via DataFileUtil """


def create_report(ctx, params, dfu):
    """ Create a simple report """
    ws_name = params['workspace_name']
    report_name = "report_" + str(uuid4())
    if 'prefix' in params:
        report_name = str(params['prefix']) + '.' + report_name
    workspace_id = dfu.ws_name_to_id(ws_name)
    # Set default empty values for various Report parameters
    report_data = {
        'objects_created': [],
        'warnings': [],
        'file_links': [],
        'html_links': [],
        'direct_html': '',
        'direct_html_link_index': 0
    }
    report_data.update(params['report'])
    save_object_params = {
        'id': workspace_id,
        'objects': [{
            'type': 'KBaseReport.Report',
            'data': report_data,
            'name': report_name,
            'meta': {},
            'hidden': 1,
            'provenance': ctx['provenance']
        }]
    }
    obj = dfu.save_objects(save_object_params)[0]
    ref = __get_object_ref(obj)
    print('object_reference', ref)
    return {
        'ref': ref,
        'name': report_name
    }


def create_extended(ctx, params, dfu):
    """
    Create an extended report
    This will upload files to shock if you provide scratch paths instead of shock_ids
    """
    # TODO
    # loop through params['file_links'] and upload all to shock
    # do the same with params['html_links']
    #   for html, zip up dirs
    validate_file_array('file_links', params.get('file_links', []))
    validate_file_array('html_links', params.get('html_links', []))
    files = fetch_or_upload_files(dfu, params.get('file_links', []))
    html_files = fetch_or_upload_files(dfu, params.get('html_links', []), zip=True)
    report_data = {
        'text_message': params.get('message', ''),
        'file_links': files,
        'html_links': html_files,
        'direct_html': params.get('direct_html', ''),  # TODO format html string base 64
        'direct_html_link_index': params.get('direct_html_link_index', 0),
        'objects_created': params.get('objects_created', []),
        'html_window_height': params.get('html_window_height'),
        'summary_window_height': params.get('summary_window_height')
    }
    report_name = params['report_object_name']
    ws_name = params['workspace_name']
    workspace_id = dfu.ws_name_to_id(ws_name)
    save_object_params = {
        'id': workspace_id,
        'objects': [{
            'type': 'KBaseReport.Report',
            'data': report_data,
            'name': report_name,
            'meta': {},
            'hidden': 1,
            'provenance': ctx['provenance']
        }]
    }
    obj = dfu.save_objects(save_object_params)[0]
    ref = __get_object_ref(obj)
    return {'ref': ref, 'name': report_name, 'shock_id': 'xyz'}


def __get_object_ref(obj):
    """ Get the reference string from an uploaded dfu object """
    return str(obj[6]) + '/' + str(obj[0]) + '/' + str(obj[4])
