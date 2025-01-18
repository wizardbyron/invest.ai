
def remove_leading_spaces(s):
    return '\n'.join([line.strip() for line in s.splitlines()])
