# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from unittest import mock

import testtools

from openstack import exceptions
from openstack.network.v2 import trunk
from openstack.tests.unit import base

EXAMPLE = {
    'id': 'IDENTIFIER',
    'description': 'Trunk description',
    'name': 'trunk-name',
    'project_id': '2',
    'admin_state_up': True,
    'port_id': 'fake_port_id',
    'status': 'ACTIVE',
    'sub_ports': [
        {
            'port_id': 'subport_port_id',
            'segmentation_id': 1234,
            'segmentation_type': 'vlan',
        }
    ],
}


class TestTrunk(base.TestCase):
    def test_basic(self):
        sot = trunk.Trunk()
        self.assertEqual('trunk', sot.resource_key)
        self.assertEqual('trunks', sot.resources_key)
        self.assertEqual('/trunks', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = trunk.Trunk(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['admin_state_up'], sot.is_admin_state_up)
        self.assertEqual(EXAMPLE['port_id'], sot.port_id)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['sub_ports'], sot.sub_ports)

    def test_add_subports_4xx(self):
        # Neutron may return 4xx for example if a port does not exist
        sot = trunk.Trunk(**EXAMPLE)
        response = mock.Mock()
        msg = '.*borked'
        response.body = {'NeutronError': {'message': msg}}
        response.json = mock.Mock(return_value=response.body)
        response.ok = False
        response.status_code = 404
        response.headers = {'content-type': 'application/json'}
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)
        subports = [
            {
                'port_id': 'abc',
                'segmentation_id': '123',
                'segmentation_type': 'vlan',
            }
        ]
        with testtools.ExpectedException(exceptions.NotFoundException, msg):
            sot.add_subports(sess, subports)

    def test_delete_subports_4xx(self):
        # Neutron may return 4xx for example if a port does not exist
        sot = trunk.Trunk(**EXAMPLE)
        response = mock.Mock()
        msg = '.*borked'
        response.body = {'NeutronError': {'message': msg}}
        response.json = mock.Mock(return_value=response.body)
        response.ok = False
        response.status_code = 404
        response.headers = {'content-type': 'application/json'}
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)
        subports = [
            {
                'port_id': 'abc',
                'segmentation_id': '123',
                'segmentation_type': 'vlan',
            }
        ]
        with testtools.ExpectedException(exceptions.NotFoundException, msg):
            sot.delete_subports(sess, subports)
