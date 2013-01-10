def debug(s, end='\n'):
    if type(s) != str and type(s) != bytes:
        s = repr(s)
    if type(s) == str:
        s = s.encode('utf-8')
    print(s, end=end)
