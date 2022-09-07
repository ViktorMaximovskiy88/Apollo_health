from backend.scrapeworker.common.state_parser import (
    guess_state_abbr,
    guess_state_name,
    guess_year_part,
)


def test_state():
    state_abbr = guess_state_abbr("PA")
    assert state_abbr == "PA"


def test_state_again_2():
    state_abbr = guess_state_abbr("PA-")
    assert state_abbr == "PA"


def test_state_again_3():
    state_abbr = guess_state_abbr("-mi-")
    assert state_abbr == "MI"


def test_state_again_4():
    state_abbr = guess_state_abbr("_PA-")
    assert state_abbr == "PA"


def test_state_again_5():
    state_name = guess_state_name("a thing in Ohio or not")
    assert state_name == "Ohio"


def test_state_again_6():
    state_name = guess_state_name("-Ohio\n")
    assert state_name == "Ohio"


def test_state_again_7():
    state_name = guess_state_name("DogsNorth CarolinaCats")
    assert state_name == "North Carolina"


def test_state_again_8():
    state_name = guess_state_name("-North Carolina_")
    assert state_name == "North Carolina"


def test_state_again_9():
    state_name = guess_state_name("\South Carolina|")
    assert state_name == "South Carolina"


def test_state_again_9():
    state_name = guess_state_name(".Michigan.")
    assert state_name == "Michigan"


def test_state_again_10():
    state_name = guess_state_name(" Michigan s")
    assert state_name == "Michigan"


def test_year_part():
    year_part = guess_year_part("OH-2022-MMP-STGRID-EN-508.pdf")
    assert year_part == 2022
