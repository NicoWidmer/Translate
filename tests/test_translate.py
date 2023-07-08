import pytest

from translate import FileHandler
from translate import Translator


@pytest.fixture
def file_handler():
    return FileHandler()


@pytest.fixture
def mock_config_ini_file(tmp_path):
    mock_file = tmp_path / "mock_config.ini"
    mock_file.write.text("Mocked content")
