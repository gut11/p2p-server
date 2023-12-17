import argparse
from node.node import start_node_server

def parse_args():
    parser = argparse.ArgumentParser(description="P2P file sharing server")

    parser.add_argument(
        "-ip",
        "--host",
        default="127.0.0.1",
        help="If given use specific host if not use default (127.0.0.1)",
    )

    parser.add_argument(
        "-dir",
        "--file-dir",
        default="./files",
        help="If given use specific dir if not use default (./files)",
    )

    args = parser.parse_args()

    return args


def main():
    args = vars(parse_args())

    print(args)
    print("salada de batata")

    start_node_server(**args)

if __name__ == "__main__":
    main()
