from argparse import ArgumentParser

def main():
    ap = ArgumentParser("simple program")
    ap.add_argument("--name", "-n", help="Name")
    args = ap.parse_args()


if __name__ == "__main__":
    main()
