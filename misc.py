# -*- coding: utf-8 -*-
"Разное"

def clean_input_string(s):
    """
    Обработка текстовых значений, введеных через гуи: 
    .strip(), unicode->string
    Речь идет о тех текстовых строках, которые и далее будут использоваться
    именно как строки.
    """
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    s = s.strip()
    return s

def unicode2str_recursively(input):
    """
    Заменить все unicode на sting во входном dict / list.
    Для обработки данный 
    """
    #stackoverflow, Mark Amery
    byteify = unicode2str_recursively
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input
