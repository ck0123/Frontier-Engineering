"""Host architecture selection must resolve real, matching release directories."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

class ToolchainArchitectureTest(unittest.TestCase):
    def test_resolve_matching_host_release(self):
        for machine, wasi, wasmtime in [
            ("aarch64", "arm64", "aarch64"),
            ("x86_64", "x86_64", "x86_64"),
        ]:
            with self.subTest(machine=machine), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                clang = root / f"wasi-sdk-34.0-{wasi}-linux/bin/clang"
                libroot = root / f"wasmtime-v48.0.2-{wasmtime}-linux-c-api"
                for path in [clang, clang.parent / "wasm-ld", libroot / "include/wasmtime.h", libroot / "include/wasm.h", libroot / "lib/libwasmtime.so"]:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.touch()
                clang.chmod(0o755)
                spec = importlib.util.spec_from_file_location("malloc_test_setup", Path(__file__).with_name("setup.py"))
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                with patch("platform.machine", return_value=machine):
                    spec.loader.exec_module(module)
                    paths = module.resolve(root)
                self.assertEqual(paths.clang, clang)
                self.assertEqual(paths.wasmtime, libroot)

if __name__ == "__main__":
    unittest.main()
