import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('planner',Path(__file__).resolve().parents[1]/'backend/planner.py');planner=importlib.util.module_from_spec(spec);spec.loader.exec_module(planner)
class Plan(unittest.TestCase):
 def test_world_preserves_pins_tags_and_removes_only_requested_name(self):
  world='foo=1-r0\nfoobar\nother@personal\n'
  marks=[{'name':'foo','action':'remove'},{'name':'new','action':'install'},{'name':'other','action':'upgrade'}]
  self.assertEqual(planner.edited_world(world,marks),'foobar\nother@personal\nnew\n')
 def test_native_output_captures_dependencies_removal_and_downgrade(self):
  data='(1/3) Installing library (1.0-r0)\n(2/3) Downgrading app (2-r0 -> 1-r0)\n(3/3) Purging old (1-r0)\nOK: 3 MiB\n'
  changes=planner.parse_changes(data);self.assertEqual(changes[0]['old'],'—');self.assertEqual(changes[1]['new'],'1-r0');self.assertEqual(changes[2]['new'],'—')
 def test_unknown_transaction_line_blocks_review(self):
  with self.assertRaises(RuntimeError):planner.parse_changes('(1/1) Unexpected action app')
 def test_rejects_invalid_or_duplicate_marks(self):
  for marks in [[{'name':'x;id','action':'install'}],[{'name':'x','action':'install'},{'name':'x','action':'remove'}]]:
   with self.assertRaises(ValueError):planner.validate_request({'marks':marks})
if __name__=='__main__':unittest.main()
