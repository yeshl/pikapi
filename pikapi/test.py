def parse(s, *args):
    print(s)
    for i in args:
        print(i)


if __name__ == "__main__":
    ss = ['1', '8', '3.', '6', '.', '18', '3.', '35', '8010']
    ip = ''.join(ss[0:-1])
    port = ss[-1]
    print(ip,port)
