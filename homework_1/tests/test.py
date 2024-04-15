import pytest

from ..log_analyzer import (
    check_errors_percent,
    get_mediana,
    get_count_perc,
    get_time_perc,
)


@pytest.mark.parametrize(
    "exeptions_counter, lines, expected",
    [
        (5000, 10000, True),
        (6000, 10000, False),
        (6000, 0, None),
    ],
)
def test_check_errors_percent(exeptions_counter, lines, expected):
    assert check_errors_percent(lines, exeptions_counter) == expected


@pytest.mark.parametrize(
    "request_time, expected",
    [
        ([1, 2, 3, 4, 5], 3),
        ([1, 2, 3, 4], 2.5),
        (["a", "d", 3, 4], None),
    ],
)
def test_get_mediana(request_time, expected):
    assert get_mediana(request_time) == expected


@pytest.mark.parametrize(
    "count, total_requests_num, expected",
    [
        (5, 10, 50),
        (6000, 0, None),
    ],
)
def test_check_get_count_perc(count, total_requests_num, expected):
    assert get_count_perc(count, total_requests_num) == expected


@pytest.mark.parametrize(
    "time_sum, total_requests_time, expected",
    [
        (5, 10, 50),
        (6000, 0, None),
    ],
)
def test_check_get_time_perc(time_sum, total_requests_time, expected):
    assert get_time_perc(time_sum, total_requests_time) == expected
