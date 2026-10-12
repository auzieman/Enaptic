import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
import sources
from native_bridge import protocol

class SourceTests(unittest.TestCase):
    def test_toggle_preserves_comments_tags_and_other_sources(self):
        text='# administrator note\n@local https://example.org/alpine/v3.24/main\n# https://example.org/disabled\n'
        disabled=sources.edit(text,dict(action='disable',index=1))
        self.assertEqual(sources.edit(disabled,dict(action='enable',index=1)),text)
        self.assertEqual(sources.edit(text,dict(action='remove',index=2)),'# administrator note\n@local https://example.org/alpine/v3.24/main\n')
    def test_url_cannot_inject_another_source_or_credentials(self):
        for url in ['https://a/\nhttps://b/','file:///etc/passwd','https://user:password@example.org','https://a/?key=x']:
            with self.assertRaises(ValueError):sources.valid_url(url)
    def test_duplicate_source_rejected(self):
        with self.assertRaises(ValueError):sources.edit('# https://example.org/repo\n',dict(action='add',url='https://example.org/repo/'))
    def test_native_protocol_counts_bytes_for_unicode(self):
        payload=protocol({'marks':[]},'example\n','example\t—\n')
        self.assertIn(str(len('example\t—\n'.encode())).encode()+b'\nexample\t',payload)
