def shorten_number(num):
    if num >= 1000000:
        short_num = f"{num / 1000000:.1f}"
    elif num >= 1000:
        short_num = f"{num / 1000:.1f}"
    else:
        return str(num)

    return short_num.rstrip('0').rstrip('.') + ('m' if num >= 1000000 else 'k')

print(round(2.5616165235125125))