def debug(s, end='\n'):
    if type(s) != str and type(s) != bytes:
        s = repr(s)
    if type(s) == bytes:
        s = s.decode('utf-8')
    print(s, end=end)
