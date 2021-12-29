import argparse


DEFAULT_PORTAL_URL="https://portaldevelop.dotypay.com"

CREATE_DEVICES_ACTION="create_devices"
ACTIVATE_DEVICES_ACTION="activate_devices"


def get_argparser():
    parser = argparse.ArgumentParser(description='Portal API helper.')

    options = {
        CREATE_DEVICES_ACTION: "Create a number of devices",
        ACTIVATE_DEVICES_ACTION: "Activate multiple devices and list their API keys. If the device is already activated then it is deactivated during the process in order to get an API key.",
    }

    subparsers = parser.add_subparsers(help=", ".join([f"{action_name}: {action_help}" for (action_name, action_help) in options.items()]), dest="action")

    create_devices_parser = subparsers.add_parser(CREATE_DEVICES_ACTION)
    create_devices_parser.add_argument("number", type=int, help="Number of devices to be created")
    create_devices_parser.add_argument("-parent_id", required=True, metavar="PARENT_BRANCH_ID", type=str, help="Parent branch ID")
    create_devices_parser.add_argument("-url", default=DEFAULT_PORTAL_URL, metavar="PORTAL_BASE_URL", type=str, help="Base Dotypay Portal URL")

    activate_devices_parser = subparsers.add_parser(ACTIVATE_DEVICES_ACTION)
    activate_devices_parser.add_argument("-first", required=True, type=int, help="ID of the first device to be activated")
    activate_devices_parser.add_argument("-last", required=True, type=int, help="ID of the last device to be activated")
    activate_devices_parser.add_argument("-url", default=DEFAULT_PORTAL_URL, metavar="PORTAL_BASE_URL", type=str, help="Base Dotypay Portal URL")

    return parser


if __name__ == "__main__":
    print(get_argparser().parse_args())
