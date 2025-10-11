def calculate_discriminant(a, b, c):
    """
    Вычисляем дискриминант квадратного уравнения
    по формуле: D = b^2 - 4*a*c
    """
    return b**2 - 4 * a * c


def main():  # pragma: no cover
    try:
        a = float(input("a = "))
        b = float(input("b = "))
        c = float(input("c = "))
    except ValueError:
        print("Ошибка ввода: необходимо вводить числа")
        return

    print("Дискриминант равен", calculate_discriminant(a, b, c))


if __name__ == "__main__":  # pragma: no cover
    main()
