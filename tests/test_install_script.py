from pathlib import Path


def test_root_install_script_installs_from_github() -> None:
    script = Path("install.sh")

    assert script.exists()
    content = script.read_text()
    assert "https://github.com/tpnthr/vllama.git" in content
    assert "uv pip install" in content
    assert "git+$REPO_URL" in content
