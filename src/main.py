import argparse
from node.node import start_node_server
from main_server.main_server import start_main_server

def parse_args():
    parser = argparse.ArgumentParser(description="P2P file sharing server")

    parser.add_argument(
        "-ms", "--mainserver", action="store_true", help="Runs a main server instance"
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=6000,
        help="If given use specific port if not use default (6000)",
    )
    parser.add_argument(
        "-ip",
        "--host",
        default="127.0.0.1",
        help="If given use specific host if not use default (127.0.0.1)",
    )

    args = parser.parse_args()

    return args


def main():
    args = vars(parse_args())
    run_main_server = args.pop("mainserver")

    if run_main_server:
        start_main_server(**args)
    else:
        start_node_server(**args)

if __name__ == "__main__":
    main()
