from pathlib import Path

from vllama.config import AppConfig, AppPaths, load_config, save_config


def test_load_config_creates_defaults_when_file_is_missing(tmp_path: Path) -> None:
    paths = AppPaths(tmp_path)

    config = load_config(paths)

    assert config.host == "127.0.0.1"
    assert config.port == 8000
    assert config.vllm_executable == "vllm"
    assert config.default_model is None
    assert paths.root.exists()
    assert paths.logs_dir.exists()


def test_save_and_reload_config_round_trips_values(tmp_path: Path) -> None:
    paths = AppPaths(tmp_path)
    config = AppConfig(
        host="0.0.0.0",
        port=8100,
        default_model="Qwen/Qwen2.5-1.5B-Instruct",
        vllm_executable="/opt/vllm/bin/vllm",
    )

    save_config(paths, config)
    reloaded = load_config(paths)

    assert reloaded == config
    assert "default_model" in paths.config_file.read_text()

