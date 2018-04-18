# -*- coding: utf-8 -*-
import unittest
import os
import time
import shutil

from DataFileUtil.DataFileUtilClient import DataFileUtil

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint  # noqa: F401

from biokbase.workspace.client import Workspace as workspaceService
from KBaseReportPy.KBaseReportPyImpl import KBaseReportPy
from KBaseReportPy.KBaseReportPyServer import MethodContext
from KBaseReportPy.authclient import KBaseAuth as _KBaseAuth
from voluptuous import MultipleInvalid


class KBaseReportPyTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('KBaseReportPy'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'KBaseReportPy',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL)
        cls.serviceImpl = KBaseReportPy(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        # Custom stuff below
        dirname = os.path.dirname(__file__)
        cls.dfu = DataFileUtil(cls.callback_url)
        cls.a_html_path = os.path.join(cls.scratch, 'a_html')
        cls.b_html_path = os.path.join(cls.scratch, 'b_html')
        shutil.copytree(os.path.join(dirname, 'data/a_html'), cls.a_html_path)
        shutil.copytree(os.path.join(dirname, 'data/b_html'), cls.b_html_path)
        cls.a_file_path = os.path.join(cls.scratch, 'a.txt')
        cls.b_file_path = os.path.join(cls.scratch, 'b.txt')
        shutil.copy2(os.path.join(dirname, 'data/a.txt'), cls.a_file_path)
        shutil.copy2(os.path.join(dirname, 'data/b.txt'), cls.b_file_path)
        # Upload files to shock
        cls.a_file_shock = cls.dfu.file_to_shock({
            'file_path': cls.a_file_path, 'make_handle': 0, 'pack': 'zip'
        })
        cls.b_file_shock = cls.dfu.file_to_shock({
            'file_path': cls.b_file_path, 'make_handle': 0, 'pack': 'zip'
        })

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_KBaseReportPy_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})  # noqa
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def check_extended_result(self, result, link_name):
        """
        Check the file upload results for an extended report
        :param result: result dictionary from running .create_extended_report
        :param link_name: one of "html_links" or "file_links"
        :returns: none
        """
        self.assertTrue(len(result[0]['ref']))
        self.assertTrue(len(result[0]['name']))
        obj = self.dfu.get_objects({'object_refs': [result[0]['ref']]})
        file_links = obj['data'][0]['data'][link_name]
        self.assertEqual(len(file_links), 2)
        self.assertEqual(file_links[0]['name'], u'a')
        self.assertEqual(file_links[1]['name'], u'b')

    @unittest.skip('x')
    def test_create(self):
        result = self.getImpl().create(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report': {
                'text_message': 'this is a test',
            }
        })
        self.assertTrue(len(result[0]['ref']))
        self.assertTrue(len(result[0]['name']))
        # TODO fetch the report using dfu by ref, check contents

    @unittest.skip('x')
    def test_create_param_errors(self):
        # See lib/KBaseReportPy/utils/validation_utils
        # We're only testing a couple examples here; there are many more error possiblities
        with self.assertRaises(MultipleInvalid) as er:
            self.getImpl().create(self.getContext(), {'report': {}})
        self.assertEqual(str(er.exception), "required key not provided @ data['workspace_name']")
        with self.assertRaises(MultipleInvalid) as er:
            self.getImpl().create(self.getContext(), {'workspace_name': 'x'})
        self.assertEqual(str(er.exception), "required key not provided @ data['report']")

    @unittest.skip('x')
    def test_create_extended_param_errors(self):
        # See lib/KBaseReportPy/utils/validation_utils
        # We're only testing a couple examples here; there are many more error possiblities
        with self.assertRaises(MultipleInvalid) as er:
            self.getImpl().create_extended_report(self.getContext(), {})
        self.assertEqual(str(er.exception), "required key not provided @ data['workspace_name']")
        with self.assertRaises(MultipleInvalid) as er:
            self.getImpl().create_extended_report(self.getContext(), {'workspace_name': 123})
        self.assertEqual(
            str(er.exception),
            "expected str for dictionary value @ data['workspace_name']"
        )

    def test_create_extended_report_with_file_paths(self):
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report_object_name': 'my_report',
            'file_links': [
                {
                    'name': 'a',
                    'description': 'a',
                    'path': self.a_file_path
                },
                {
                    'name': 'b',
                    'description': 'b',
                    'path': self.b_file_path
                }
            ]
        })
        self.check_extended_result(result, 'file_links')

    def test_create_extended_report_with_uploaded_files(self):
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report_object_name': 'my_report',
            'file_links': [
                {
                    'name': 'a',
                    'description': 'a',
                    'shock_id': self.a_file_shock['shock_id']
                },
                {
                    'name': 'b',
                    'description': 'b',
                    'shock_id': self.b_file_shock['shock_id']
                }
            ]
        })
        self.check_extended_result(result, 'file_links')

    def test_create_extended_report_with_uploaded_html_files(self):
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report_object_name': 'my_report',
            'html_links': [
                {
                    'name': 'a',
                    'description': 'a',
                    'shock_id': self.a_file_shock['shock_id']
                },
                {
                    'name': 'b',
                    'description': 'b',
                    'shock_id': self.b_file_shock['shock_id']
                }
            ]
        })
        self.check_extended_result(result, 'html_links')

    def test_create_extended_report_with_html_paths(self):
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report_object_name': 'my_report',
            'file_links': [
                {
                    'name': 'a',
                    'description': 'a',
                    'path': self.a_file_path
                },
                {
                    'name': 'b',
                    'description': 'b',
                    'path': self.b_file_path
                }
            ]
        })
        self.check_extended_result(result, 'file_links')
