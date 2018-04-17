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
        cls.dfu = DataFileUtil(cls.callback_url)

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

    def getDfu(self):
        return DataFileUtil(self.callback_url)

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

    def test_create_param_errors(self):
        # See lib/KBaseReportPy/utils/validation_utils
        # We're only testing a couple examples here; there are many more error possiblities
        with self.assertRaises(MultipleInvalid) as er:
            self.getImpl().create(self.getContext(), {'report': {}})
        self.assertEqual(str(er.exception), "required key not provided @ data['workspace_name']")
        with self.assertRaises(MultipleInvalid) as er:
            self.getImpl().create(self.getContext(), {'workspace_name': 'x'})
        self.assertEqual(str(er.exception), "required key not provided @ data['report']")

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
        dirname = os.path.dirname(__file__)
        a_path = os.path.join(self.scratch, 'a.txt')
        b_path = os.path.join(self.scratch, 'b.txt')
        shutil.copy2(os.path.join(dirname, 'data/a.txt'), a_path)
        shutil.copy2(os.path.join(dirname, 'data/b.txt'), b_path)
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report_object_name': 'my_report',
            'file_links': [
                {
                    'name': 'a',
                    'description': 'a',
                    'path': a_path
                },
                {
                    'name': 'b',
                    'description': 'b',
                    'path': b_path
                }
            ]
        })
        self.assertTrue(len(result[0]['ref']))
        self.assertTrue(len(result[0]['name']))
        obj = self.dfu.get_objects({'object_refs': [result[0]['ref']]})
        file_links = obj['data'][0]['data']['file_links']
        self.assertEqual(len(file_links), 2)
        self.assertEqual(file_links[0]['name'], u'a')
        self.assertEqual(file_links[1]['name'], u'b')

    def test_create_extended_report_with_uploaded_files(self):
        dirname = os.path.dirname(__file__)
        a_path = os.path.join(self.scratch, 'a.txt')
        b_path = os.path.join(self.scratch, 'b.txt')
        shutil.copy2(os.path.join(dirname, 'data/a.txt'), a_path)
        shutil.copy2(os.path.join(dirname, 'data/b.txt'), b_path)
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report_object_name': 'my_report',
            'file_links': [
                {
                    'name': 'a',
                    'description': 'a',
                    'path': a_path
                },
                {
                    'name': 'b',
                    'description': 'b',
                    'path': b_path
                }
            ]
        })
        self.assertTrue(len(result[0]['ref']))
        self.assertTrue(len(result[0]['name']))
        # TODO test that file links with paths get uploaded
        # TODO test that html links with paths get zipped and uploaded

    def test_create_extended_report_with_html_paths(self):
        dirname = os.path.dirname(__file__)
        a_path = os.path.join(self.scratch, 'a.html')
        b_path = os.path.join(self.scratch, 'b.html')
        shutil.copy2(os.path.join(dirname, 'data/a.html'), a_path)
        shutil.copy2(os.path.join(dirname, 'data/b.html'), b_path)
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report_object_name': 'my_report',
            'html_links': [
                {
                    'name': 'a',
                    'description': 'a',
                    'path': a_path
                },
                {
                    'name': 'b',
                    'description': 'b',
                    'path': b_path
                }
            ]
        })
        self.assertTrue(len(result[0]['ref']))
        self.assertTrue(len(result[0]['name']))
        # TODO test that file links with paths get uploaded
        # TODO test that html links with paths get zipped and uploaded
