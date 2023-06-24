import random, string


def generate_password(name):
    lower = name.lower()
    upper = name.upper()
    num = string.digits
    symbols = string.punctuation
    all = num + symbols

    password_part1 = ''.join(random.choice(lower) for i in range(4))
    password_part2 = ''.join(random.choice(upper) for i in range(4))
    password_part3 = ''.join(random.choice(all) for i in range(4))

    password = password_part1 + password_part2 + password_part3
    return password