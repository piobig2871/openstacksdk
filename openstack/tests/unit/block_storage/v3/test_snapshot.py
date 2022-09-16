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

from keystoneauth1 import adapter

from openstack.block_storage.v3 import snapshot
from openstack.tests.unit import base


FAKE_ID = "ffa9bc5e-1172-4021-acaf-cdcd78a9584d"

SNAPSHOT = {
    "status": "creating",
    "description": "Daily backup",
    "created_at": "2015-03-09T12:14:57.233772",
    "updated_at": None,
    "metadata": {},
    "volume_id": "5aa119a8-d25b-45a7-8d1b-88e127885635",
    "size": 1,
    "id": FAKE_ID,
    "name": "snap-001",
    "force": "true",
    "os-extended-snapshot-attributes:progress": "100%",
    "os-extended-snapshot-attributes:project_id":
        "0c2eba2c5af04d3f9e9d0d410b371fde"
}


class TestSnapshot(base.TestCase):

    def test_basic(self):
        sot = snapshot.Snapshot(SNAPSHOT)
        self.assertEqual("snapshot", sot.resource_key)
        self.assertEqual("snapshots", sot.resources_key)
        self.assertEqual("/snapshots", sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual({"name": "name",
                              "status": "status",
                              "all_projects": "all_tenants",
                              "project_id": "project_id",
                              "volume_id": "volume_id",
                              "limit": "limit",
                              "marker": "marker"},
                             sot._query_mapping._mapping)

    def test_create_basic(self):
        sot = snapshot.Snapshot(**SNAPSHOT)
        self.assertEqual(SNAPSHOT["id"], sot.id)
        self.assertEqual(SNAPSHOT["status"], sot.status)
        self.assertEqual(SNAPSHOT["created_at"], sot.created_at)
        self.assertEqual(SNAPSHOT["updated_at"], sot.updated_at)
        self.assertEqual(SNAPSHOT["metadata"], sot.metadata)
        self.assertEqual(SNAPSHOT["volume_id"], sot.volume_id)
        self.assertEqual(SNAPSHOT["size"], sot.size)
        self.assertEqual(SNAPSHOT["name"], sot.name)
        self.assertEqual(
            SNAPSHOT["os-extended-snapshot-attributes:progress"],
            sot.progress)
        self.assertEqual(
            SNAPSHOT["os-extended-snapshot-attributes:project_id"],
            sot.project_id)
        self.assertTrue(sot.is_forced)


class TestSnapshotActions(base.TestCase):

    def setUp(self):
        super(TestSnapshotActions, self).setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.resp.headers = {}
        self.resp.status_code = 202

        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.get = mock.Mock()
        self.sess.post = mock.Mock(return_value=self.resp)
        self.sess.default_microversion = None

    def test_force_delete(self):
        sot = snapshot.Snapshot(**SNAPSHOT)

        self.assertIsNone(sot.force_delete(self.sess))

        url = 'snapshots/%s/action' % FAKE_ID
        body = {'os-force_delete': {}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_reset(self):
        sot = snapshot.Snapshot(**SNAPSHOT)

        self.assertIsNone(sot.reset(self.sess, 'new_status'))

        url = 'snapshots/%s/action' % FAKE_ID
        body = {'os-reset_status': {'status': 'new_status'}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_set_status(self):
        sot = snapshot.Snapshot(**SNAPSHOT)

        self.assertIsNone(sot.set_status(self.sess, 'new_status'))

        url = 'snapshots/%s/action' % FAKE_ID
        body = {'os-update_snapshot_status': {'status': 'new_status'}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)
