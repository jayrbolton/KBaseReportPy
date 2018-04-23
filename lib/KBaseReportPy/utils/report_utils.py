# -*- coding: utf-8 -*-
from file_utils import validate_paths, fetch_or_upload_files
from uuid import uuid4

""" Utilities for creating reports using DataFileUtil """


def create_report(ctx, params, dfu):
    """
    Create a simple report
    :param ctx: context dict passed into KBaseReportImpl#create
    :param params: see utils/validation_utils
    :param dfu: instance of DataFileUtil
    :returns: report data
    """
    report_name = "report_" + str(uuid4())
    workspace_id = _get_workspace_id(dfu, params)
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
    ref = _get_object_ref(obj)
    return {'ref': ref, 'name': report_name}


def create_extended(ctx, params, dfu):
    """
    Create an extended report
    This will upload files to shock if you provide scratch paths instead of shock_ids
    :param ctx: context dict passed from KBaseReportImpl#create
    :param params: see utils/validation_utils and the KIDL spec
    :param dfu: instance of DataFileUtil
    :returns: uploaded report data
    """
    validate_paths('file_links', params.get('file_links', []))
    validate_paths('html_links', params.get('html_links', []))
    files = fetch_or_upload_files(dfu, params.get('file_links', []))  # see ./file_utils.py
    html_files = fetch_or_upload_files(dfu, params.get('html_links', []), zip=True)
    report_data = {
        'text_message': params.get('message', ''),
        'file_links': files,
        'html_links': html_files,
        'direct_html': params.get('direct_html', ''),
        'direct_html_link_index': params.get('direct_html_link_index', 0),
        'objects_created': params.get('objects_created', []),
        'html_window_height': params.get('html_window_height'),
        'summary_window_height': params.get('summary_window_height')
    }
    report_name = params.get('report_object_name', 'report_' + str(uuid4()))
    workspace_id = _get_workspace_id(dfu, params)
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
    ref = _get_object_ref(obj)
    return {'ref': ref, 'name': report_name, 'shock_id': 'xyz'}


def _get_workspace_id(dfu, params):
    """
    Get the workspace ID from the params, which may either have 'workspace_id'
    or 'workspace_name'
    """
    if 'workspace_name' in params:
        return dfu.ws_name_to_id(params['workspace_name'])
    else:
        return params['workspace_id']


def _get_object_ref(obj):
    """ Get the reference string from an uploaded dfu object """
    return str(obj[6]) + '/' + str(obj[0]) + '/' + str(obj[4])
