import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
import flatpak_backend as fp

class FlatpakTests(unittest.TestCase):
    def test_identity_retains_scope_remote_kind_and_branch(self):
        token=fp.identity('user','flathub','app/org.example.App/x86_64/stable')
        self.assertEqual(fp.decode(token),dict(scope='user',origin='flathub',ref='app/org.example.App/x86_64/stable'))
        self.assertNotEqual(token,fp.identity('system','flathub','app/org.example.App/x86_64/stable'))
        self.assertNotEqual(token,fp.identity('user','flathub','app/org.example.App/x86_64/beta'))
    def test_invalid_ref_and_scope_fail_before_commands(self):
        for scope,ref in [('root','app/org.example.App/x86_64/stable'),('user','app/../../etc/passwd'),('user','app/org.example.App/x86_64/stable;id')]:
            with self.assertRaises(ValueError):fp.decode(fp.identity(scope,'flathub',ref))
    def test_catalog_keeps_available_and_installed_rows_distinct(self):
        def run(scope,command,*args):
            if scope=='user' or '--runtime' in args:return ''
            if '--updates' in args:return 'org.example.App/x86_64/stable\tflathub\n'
            if command=='list':return 'app/org.example.App/x86_64/stable\tExample\t1.0\tflathub\tPlayer\tabcdef\n'
            return 'org.example.App/x86_64/stable\tExample\t2.0\tflathub\tPlayer\t123456\norg.example.App/x86_64/beta\tExample Beta\t3.0\tflathub\tPlayer\t987654\n'
        with patch.object(fp,'run',side_effect=run),patch.object(fp.shutil,'which',return_value='/usr/bin/flatpak'):
            catalog,warnings=fp.catalog()
        self.assertFalse(warnings);self.assertEqual(len(catalog),2)
        stable=next(p for p in catalog if fp.decode(p['identity'])['ref'].endswith('/stable'))
        beta=next(p for p in catalog if fp.decode(p['identity'])['ref'].endswith('/beta'))
        self.assertTrue(stable['upgradable']);self.assertEqual(stable['installed'],'1.0');self.assertEqual(beta['installed'],'—')
    def test_malformed_columns_rejected(self):
        with self.assertRaises(RuntimeError):fp.rows('bad\tcolumns',6)
