# -*- coding: utf-8 -*-
"Разные функции для работы с кодировкой и тому подобное"

import json

def U(s):
    "run-time utf-8 -> unicode"
    return unicode(s, 'utf-8')

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

def limit_text_len(text, max_len, allow_multiline):
    """
    Обрезает строку, если ее длина превышает заданную, и ставит '...' .
    Аргументы:
        text (str)
        max_len (int)
        allow_multiline (bool): если False, то обрежет до первого '\n'
    Возвращает:
        tuple (str, bool)
        где последний элемент True, если производилась обрезка
    """
    mod_text = text

    lines_cut = False
    if not allow_multiline:
        text_lines = mod_text.split('\n')
        if len(text_lines) > 1:
            for tl in text_lines[2:]:
                if len(tl) > 0:
                    lines_cut = True
                    break
        mod_text = text_lines[0]
        
    mod_text_unicode = unicode(mod_text, 'utf-8')
    len_cut = len(mod_text_unicode) > max_len
    if len_cut:
        mod_text = mod_text_unicode[0:max_len].encode('utf-8')
    if (lines_cut or len_cut):
        mod_text =  mod_text +  ' ...'

    return (mod_text, (lines_cut or len_cut))


