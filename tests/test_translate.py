import pytest
from translate import FileHandler
from translate import Translator


@pytest.fixture
def file_handler():
    return FileHandler()


@pytest.fixture
def mock_config_ini_file_string():
    file_content = ";; Add more entries to support additional languages to upload\n" \
                   ";; Left: Language code in file name (DeepL language code)\n" \
                   ";; Right: Youtube language code\n" \
                   "\n" \
                   "[LANGUAGES]\n" \
                   "bg = bg\n" \
                   "cs = cs\n" \
                   "de = de\n" \
                   "el = el\n" \
                   "es = es\n" \
                   "fi = fi\n" \
                   "fr = fr\n" \
                   "hu = hu\n" \
                   "id = id\n" \
                   "it = it\n" \
                   "ja = ja\n" \
                   "ko = ko\n" \
                   "nb = no\n" \
                   "nl = nl\n" \
                   "pl = pl\n" \
                   "pt - br = pt - Br\n" \
                   "ro = ro\n" \
                   "ru = ru\n" \
                   "sv = sv\n" \
                   "tr = tr\n" \
                   "uk = uk\n" \
                   "zh = zh - Hans\n" \
                   "\n" \
                   "; Nothing will get translated after this character\n" \
                   "[PROPERTIES]\n" \
                   "end_translation_character = 🎵\n"

    return file_content

@pytest.fixture
def mock_config_ini_file(tmp_path):
    file_path = tmp_path / "config.ini"
    file_content = ";; Add more entries to support additional languages to upload\n" \
                   ";; Left: Language code in file name (DeepL language code)\n" \
                   ";; Right: Youtube language code\n" \
                   "\n" \
                   "[LANGUAGES]\n" \
                   "bg = bg\n" \
                   "cs = cs\n" \
                   "de = de\n" \
                   "el = el\n" \
                   "es = es\n" \
                   "fi = fi\n" \
                   "fr = fr\n" \
                   "hu = hu\n" \
                   "id = id\n" \
                   "it = it\n" \
                   "ja = ja\n" \
                   "ko = ko\n" \
                   "nb = no\n" \
                   "nl = nl\n" \
                   "pl = pl\n" \
                   "pt - br = pt - Br\n" \
                   "ro = ro\n" \
                   "ru = ru\n" \
                   "sv = sv\n" \
                   "tr = tr\n" \
                   "uk = uk\n" \
                   "zh = zh - Hans\n" \
                   "\n" \
                   "; Nothing will get translated after this character\n" \
                   "[PROPERTIES]\n" \
                   "end_translation_character = 🎵\n"

    file_path.write_text(file_content)

    return file_path


def test_read_config_file_languages(mock_config_ini_file):
    file_handler = FileHandler()
    file_handler.read_config_file(mock_config_ini_file)
    languages_correct = True

    for language in file_handler.languages:
        if language not in mock_config_ini_file:
            languages_correct = False
            break

    assert languages_correct


def test_read_config_file_end_translation_char(mock_config_ini_file):
    file_handler = FileHandler()
    file_handler.read_config_file(mock_config_ini_file)

    assert file_handler.end_translation_character in mock_config_ini_file
