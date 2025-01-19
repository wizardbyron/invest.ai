
DISCLIAMER = """本站用于实验目的，不构成任何投资建议，也不作为任何法律法规、监管政策的依据，投资者不应以该等信息作为决策依据或依赖该等信息做出法律行为，由此造成的一切后果由投资者自行承担。"""


def remove_leading_spaces(s):
    return '\n'.join([line.strip() for line in s.splitlines()])
