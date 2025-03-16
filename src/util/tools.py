

def remove_leading_spaces(s: str) -> str:
    """删除文本中的前导空格

    Args:
        s (_type_): 输入字符串

    Returns:
        _type_: _description_
    """
    return '\n'.join([line.strip() for line in s.splitlines()])


def append_discliamer(md_text: str) -> str:
    """markdown 文本末尾增加免责声明

    Args:
        md_text (str): _description_

    Returns:
        str: _description_
    """    """"""

    output = f"""{md_text}

    ## 免责声明
    
    以上内容由人工智能大语言模型生成，并用于研究实验目的。
    其内容不构成任何投资建议，也不作为任何法律法规、监管政策的依据。
    投资者不应以该等信息作为决策依据或依赖该等信息做出法律行为，由此造成的一切后果由投资者自行承担。
    """

    return remove_leading_spaces(output)
