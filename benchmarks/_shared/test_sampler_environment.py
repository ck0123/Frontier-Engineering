"""Sampler children must preserve the evaluator's no-bytecode policy."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sampler_isolation

class SamplerEnvironmentTest(unittest.TestCase):
    def test_no_bytecode_policy_reaches_real_isolated_child(self):
        with tempfile.TemporaryDirectory() as directory:
            driver = Path(directory) / 'driver.py'
            driver.write_text("import json, sys\nfrom pathlib import Path\nPath('result.json').write_text(json.dumps({'no_bytecode': sys.dont_write_bytecode}))\n")
            with patch.dict(os.environ, {'PYTHONDONTWRITEBYTECODE': '1'}):
                run = sampler_isolation.sandbox.run_candidate_isolated(
                    driver, expected_outputs=('result.json',), timeout_s=20,
                    env_allowlist=sampler_isolation.ENV_ALLOWLIST,
                )
            self.assertEqual(run.returncode, 0, run.stderr_tail)
            self.assertTrue(json.loads(run.read_output_bytes('result.json'))['no_bytecode'])

if __name__ == '__main__':
    unittest.main()
