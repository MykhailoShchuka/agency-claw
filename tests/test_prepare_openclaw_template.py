from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import Mock

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT.parent / "agency-swarm" / "src"))

import prepare_openclaw_template as prepare_module


def test_prepare_openclaw_template_writes_control_ui_allowed_origins(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_HOME", str(tmp_path / "openclaw"))
    monkeypatch.setenv(
        "OPENCLAW_CONTROL_UI_ALLOWED_ORIGINS_JSON",
        json.dumps(
            [
                "https://agentswarm.ai",
                "http://localhost:8082",
            ]
        ),
    )
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "gateway-token")
    monkeypatch.setattr(prepare_module.shutil, "which", Mock(return_value="/usr/local/bin/openclaw"))
    validate_run = Mock(return_value=Mock())
    monkeypatch.setattr(prepare_module.subprocess, "run", validate_run)

    config = prepare_module.prepare_openclaw_template()
    payload = json.loads(config.config_path.read_text(encoding="utf-8"))
    second_config = prepare_module.prepare_openclaw_template()
    second_payload = json.loads(second_config.config_path.read_text(encoding="utf-8"))

    assert payload["gateway"]["controlUi"]["allowedOrigins"] == [
        "https://agentswarm.ai",
        "http://localhost:8082",
    ]
    assert payload["gateway"]["auth"]["token"] == "gateway-token"
    assert payload["agents"]["defaults"]["workspace"] == str(config.workspace_dir)
    assert second_config.config_path == config.config_path
    assert second_payload == payload
    assert validate_run.call_count == 2
    validate_run.assert_called_with(
        ["/usr/local/bin/openclaw", "config", "validate"],
        check=True,
        capture_output=True,
        text=True,
        env={
            **prepare_module.os.environ,
            "OPENCLAW_CONFIG_PATH": str(config.config_path),
            "OPENCLAW_HOME": str(config.home_dir),
        },
    )
