import pytest
from discriminant import calculate_discriminant


# Позитивные тесты, когда D >= 0
@pytest.mark.parametrize("a,b,c,expected", [
    (1, -3, 2, 1),    # x^2 - 3x + 2 = 0, соответственно D = 9 - 8 = 1
    (1, 2, 1, 0),     # x^2 + 2x + 1 = 0, соответственно D = 4 - 4 = 0
    (2, 5, 2, 9)  # 2x^2 + 5x + 2, соответственно D = 25 - 16 = 9
])
def test_discriminant_positive(a, b, c, expected):
    assert calculate_discriminant(a, b, c) == expected


# Негативные тесты, когда D < 0
@pytest.mark.parametrize("a,b,c", [
    (1, 0, 1),      # x^2 + 1 = 0, D = -4
    (3, 2, 3)       # D = 4 - 36 = -32
])
def test_discriminant_negative(a, b, c):
    assert calculate_discriminant(a, b, c) < 0
