import sys
from argparse import ArgumentParser


def main():
    ap = ArgumentParser("simple program")
    ap.add_argument("--name", "-n", help="Name")
    args = ap.parse_args()
    print("OName:", args.name)
    with open("output.txt", "w") as f:
        f.write("FName: " + args.name + "\n")
    print("EName:", args.name, file=sys.stderr)


if __name__ == "__main__":
    main()
