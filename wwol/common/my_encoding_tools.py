# -*- coding: utf-8 -*-
"""
Разные функции для работы с кодировкой и тому подобное.

Устаревшее поведение (версия 0.2, Питон 2.7) было следующим:
Внутри программы все текстовые данные передаются в типе str и кодировке UTF8.
GUI и функции I/O работают с типом unicode.
Запуска внешний программ работает через local_encoding.
"""

import locale
import sys

_local_encoding = locale.getpreferredencoding()
ON_APPLE = (sys.platform == 'darwin')

def U(s):
    "run-time utf-8 -> unicode"
    if isinstance(s, str):
        return s
    else:
        return str(s, 'utf-8')

def local_encoding(s):
    "Эта функция ничего не делает (для совместимости со старой версией)"
    return s

def local_encoding_b(s):
    "str | utf-8-bytes  -> bytes"
    return U(s).encode(_local_encoding)
        
def clean_input_string(s):
    """
    Обработка текстовых значений, введеных через гуи
    Речь идет о тех текстовых строках, которые и далее будут использоваться
    именно как строки. 
    (Раньше в питоне 2, здесь еще разруливались проблемы с Юникодом) 
    """
    s = s.strip()
    #  неожиданная проблема с прямыми и красивыми кавычками
    if ON_APPLE:  # TODO:  проверить другие платформы
        s = s.replace('\xab','"').replace('\xbb','"')
        s = s.replace('‘','\"')
    return s

def unicode2str_recursively(input):
    """
    Устаревашя функция
    В питоне 2 здесь мы заменяли все unicode на sting во входном dict / list.
    Теперь не делаем ничего
    """
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
        
    mod_text_unicode = str(mod_text, 'utf-8')
    len_cut = len(mod_text_unicode) > max_len
    if len_cut:
        mod_text = mod_text_unicode[0:max_len].encode('utf-8')
    if (lines_cut or len_cut):
        mod_text =  mod_text +  ' ...'

    return (mod_text, (lines_cut or len_cut))

def fname2quotes(s):
    "Сначала удаляет из строки кавычки, затем обертывает ее кавычки, когда надо."
    s = ''.join(s.split('"'))
    if s.find(' ') >= 0 or s.find("'") >= 0 or len(s) == 0:
        s = '"' + s + '"'
    return s
    
def double_backslash(s):
    "удваивает все слэши \\ , чтобы не было эскейп-последовательности"
    pos = 0
    while pos < len(s):
        pos = s.find('\\', pos)
        if pos < 0: break
        s = s[:pos] + '\\' + s[pos:]
        pos = pos + 2
    return s
