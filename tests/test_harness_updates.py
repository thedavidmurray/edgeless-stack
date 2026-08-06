import subprocess
import unittest

class TestHarnessUpdates(unittest.TestCase):
    def test_fusion_workflow(self):
        # Run the fusion_workflow script and check output contains merged marker
        result = subprocess.run(['python', 'hooks/fusion_workflow.py'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('[FUSED]', result.stdout)

    def test_validation_gate_placeholder(self):
        # Run the validation_gate placeholder (if exists) and expect it to exit 0
        result = subprocess.run(['python', 'hooks/validation_gate.py'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)

if __name__ == '__main__':
    unittest.main()
