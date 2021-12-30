from playwright.sync_api import sync_playwright
import os

import args
from portal import DotypayPortal
from args import CREATE_DEVICES_ACTION
from args import ACTIVATE_DEVICES_ACTION


def process_activate_devices_action(args, portal):
    if args.first > 0 and args.last > 0 and args.first <= args.last:
        api_keys = portal.activate_devices(args.first, args.last)
        print("New API keys:")
        for (name, api_key) in api_keys:
            print(f"{name}: {api_key}")
    else:
        print("The range must start on greater index than zero and the end must be greater or equal than the start.")
    

def process_create_devices_action(args, portal):
    if args.number > 0:
        portal.create_new_devices(args.number, args.parent_id)
    else:
        print("Cannot create zero or negative number of devices!")


def process_args(args, username, password):
    with sync_playwright() as p:
        # initialize a browser and the Portal wrapper
        browser = p.chromium.launch()
        portal = DotypayPortal(browser, args.url, username, password)

        if args.action == CREATE_DEVICES_ACTION:
            process_create_devices_action(args, portal)
        elif args.action == ACTIVATE_DEVICES_ACTION:
            process_activate_devices_action(args, portal)
        else:
            print("Unknown action, see some help.")

        browser.close()


if __name__ == "__main__":
    if "PORTAL_USERNAME" in os.environ and "PORTAL_PASSWORD" in os.environ:
        args = args.get_argparser().parse_args()
        process_args(args, os.environ["PORTAL_USERNAME"], os.environ["PORTAL_PASSWORD"])
    else:
        print("Both PORTAL_USERNAME and PORTAL_PASSWORD env. variables have to be set.")
    
