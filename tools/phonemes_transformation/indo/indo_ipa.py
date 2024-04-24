from g2p_id import G2P

def g2p(text):
    g2p = G2P()
    return g2p(text)


if __name__ == '__main__':
    # print(g2p("menyisir rambut"))

    # alpha = "abcdefghijklmnopqrstuvwxyz"

    # for c in alpha:
    #     print(f'{c} -> {g2p(c)}')
    while True:
        c = input()
        print(g2p(c))