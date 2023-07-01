import pytest

from translate import FileHandler
from translate import Translator

@pytest.fixture
def file_handler():
    return FileHandler()