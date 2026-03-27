import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import openclaw_runtime_bootstrap as bootstrap


class EnsureOpenClawRuntimeTests(unittest.TestCase):
    @patch("openclaw_runtime_bootstrap._bootstrap_runtime")
    @patch("openclaw_runtime_bootstrap._ensure_minimal_config_file")
    @patch("openclaw_runtime_bootstrap._resolve_bootstrap_home_dir", return_value=Path("/tmp/openclaw"))
    @patch("openclaw_runtime_bootstrap.shutil.which", return_value="/usr/local/bin/openclaw")
    def test_invalid_gateway_command_uses_installed_openclaw(
        self,
        which_mock,
        resolve_home_mock,
        ensure_config_mock,
        bootstrap_runtime_mock,
    ) -> None:
        with patch.dict(os.environ, {"OPENCLAW_GATEWAY_COMMAND": '"openclaw gateway'}, clear=False):
            bootstrap.ensure_openclaw_runtime()
            self.assertEqual(os.environ["OPENCLAW_GATEWAY_COMMAND"], "/usr/local/bin/openclaw gateway run")

        bootstrap_runtime_mock.assert_not_called()
        resolve_home_mock.assert_called_once()
        ensure_config_mock.assert_called_once_with(Path("/tmp/openclaw"))
        which_mock.assert_called_once_with("openclaw")

    @patch("openclaw_runtime_bootstrap._export_runtime")
    @patch(
        "openclaw_runtime_bootstrap._bootstrap_runtime",
        return_value=SimpleNamespace(openclaw_bin=Path("/tmp/openclaw/.runtime/openclaw/bin/openclaw")),
    )
    @patch("openclaw_runtime_bootstrap._ensure_minimal_config_file")
    @patch("openclaw_runtime_bootstrap._resolve_bootstrap_home_dir", return_value=Path("/tmp/openclaw"))
    @patch("openclaw_runtime_bootstrap.shutil.which", return_value=None)
    def test_invalid_gateway_command_bootstraps_when_cli_missing(
        self,
        which_mock,
        resolve_home_mock,
        ensure_config_mock,
        bootstrap_runtime_mock,
        export_runtime_mock,
    ) -> None:
        with patch.dict(os.environ, {"OPENCLAW_GATEWAY_COMMAND": '"openclaw gateway'}, clear=False):
            bootstrap.ensure_openclaw_runtime()

        bootstrap_runtime_mock.assert_called_once_with(Path("/tmp/openclaw"), "22.22.1", "2026.3.23-2")
        export_runtime_mock.assert_called_once()
        ensure_config_mock.assert_called_once_with(Path("/tmp/openclaw"))
        resolve_home_mock.assert_called_once()
        which_mock.assert_called_once_with("openclaw")


if __name__ == "__main__":
    unittest.main()
