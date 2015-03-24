# -*- coding: utf-8 -*-
"Разное"

def clean_input_string(s):
    """
    Обработка текстовых значений, введеных через гуи: 
    .strip(), unicode->string
    Речь идет о тех текстовых строках, которые и далее будут использоваться
    как строки.
    """
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    s = s.strip()
    return s
