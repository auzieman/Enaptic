import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('backend',Path(__file__).resolve().parents[1]/'backend/apk_backend.py');backend=importlib.util.module_from_spec(spec);spec.loader.exec_module(backend)
class Catalog(unittest.TestCase):
 def test_native_candidates_upgrade_flags_and_installed_only(self):
  old=[dict(name='kept',version='9-r0'),dict(name='orphan',version='1-r0')]
  new=[dict(name='kept',version='10-r0',repositories=['https://example/community'],origin='source-kept'),dict(name='fresh',version='1-r0')]
  with patch.object(backend,'query',side_effect=[old,new,[dict(name='kept')]]):rows={r['name']:r for r in backend.catalog()}
  self.assertEqual(rows['kept']['candidate'],'10-r0');self.assertTrue(rows['kept']['upgradable']);self.assertEqual(rows['kept']['repository'],'https://example/community');self.assertEqual(rows['orphan']['candidate'],'—');self.assertEqual(rows['fresh']['installed'],'—')
 def test_rejects_package_constraint_as_detail_name(self):
  with self.assertRaises(ValueError):backend.details('apk-tools;id')
if __name__=='__main__':unittest.main()
