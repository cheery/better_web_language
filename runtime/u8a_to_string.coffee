# http://www.onicos.com/staff/iz/amuse/javascript/expert/utf.txt

# utf.js - UTF-8 <=> UTF-16 convertion
# 
# Copyright (C) 1999 Masanao Izumo <iz@onicos.co.jp>
# Version: 1.0
# LastModified: Dec 25 1999
# This library is free.  You can redistribute it and/or modify it.
# 
# Translated to coffeescript.
# Added choice to pick range to translate from.
# If this was C, it would have potential overflow bug. btw.

betterweb.utf8ToString = (array, start=0, stop=array.length) ->
    out = ""
    i = start
    while i < stop
        c = array[i++]
        d = c >> 4
        if c < 128 # 0xxxxxxx
            out += String.fromCharCode(c)
        else if d == 12 or d == 13 # 110x xxxx   10xx xxxx
            char2 = array[i++]
            out += String.fromCharCode(((c & 0x1F) << 6) | (char2 & 0x3F))
        else if d == 14
            # 1110 xxxx  10xx xxxx  10xx xxxx
            char2 = array[i++]
            char3 = array[i++]
            out += String.fromCharCode(((c & 0x0F) << 12) |
                           ((char2 & 0x3F) << 6) |
                           ((char3 & 0x3F) << 0))
        else
            throw "XXX: utf-8 decoding error?"
    return out
