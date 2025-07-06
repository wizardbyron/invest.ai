from src.util import numbers_in_chinese, add_spaces_in_str


def test_numbers_in_chinese():
    assert numbers_in_chinese('123') == ('一二三')


def test_add_spaces_in_str():
    assert add_spaces_in_str('123') == ('1 2 3')
    assert add_spaces_in_str('UVIX') == ('U V I X')
