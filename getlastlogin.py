#! /usr/bin/env python

"""
Prisma SDWAN Confidentail
Get Operators Last Login Data
tkamath@paloaltonetworks.com
"""

import cloudgenix
import csv
import pandas as pd
import argparse
import sys
import os
import datetime


SDK_VERSION = cloudgenix.version
SCRIPT_NAME = 'Prisma SDWAN: Operators Last Login'


sys.path.append(os.getcwd())
try:
    from cloudgenix_settings import CLOUDGENIX_AUTH_TOKEN
    print(CLOUDGENIX_AUTH_TOKEN)

except ImportError:
    # Get AUTH_TOKEN/X_AUTH_TOKEN from env variable, if it exists. X_AUTH_TOKEN takes priority.
    if "X_AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('X_AUTH_TOKEN')
    elif "AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
    else:
        # not set
        CLOUDGENIX_AUTH_TOKEN = None

try:
    from cloudgenix_settings import CLOUDGENIX_USER, CLOUDGENIX_PASSWORD

except ImportError:
    # will get caught below
    CLOUDGENIX_USER = None
    CLOUDGENIX_PASSWORD = None


def getdatefromepoch(x):
    ts = datetime.datetime.utcfromtimestamp(x/10000000)
    return ts.isoformat()


def go():
    ############################################################################
    # Begin Script, start login / argument handling.
    ############################################################################
    # Parse arguments
    parser = argparse.ArgumentParser(description="{0}.".format(SCRIPT_NAME))

    # Allow Controller modification and debug level sets.
    controller_group = parser.add_argument_group('API', 'These options change how this program connects to the API.')
    controller_group.add_argument("--controller", "-C",
                                  help="Controller URI, ex. "
                                       "C-Prod: https://api.cloudgenix.com",
                                  default=None)

    controller_group.add_argument("--insecure", "-I", help="Disable SSL certificate and hostname verification",
                                  dest='verify', action='store_false', default=True)

    login_group = parser.add_argument_group('Login', 'These options allow skipping of interactive login')
    login_group.add_argument("--email", "-E", help="Use this email as User Name instead of prompting",
                             default=None)
    login_group.add_argument("--pass", "-PW", help="Use this Password instead of prompting",
                             default=None)

    debug_group = parser.add_argument_group('Debug', 'These options enable debugging output')
    debug_group.add_argument("--debug", "-D", help="Verbose Debug info, levels 0-2", type=int,
                             default=0)

    args = vars(parser.parse_args())

    ############################################################################
    # Instantiate API
    ############################################################################
    cgx_session = cloudgenix.API(controller=args["controller"], ssl_verify=False)
    cgx_session.set_debug(args["debug"])

    ############################################################################
    # Draw Interactive login banner, run interactive login including args above.
    ############################################################################

    print("{0} v{1} ({2})\n".format(SCRIPT_NAME, SDK_VERSION, cgx_session.controller))

    # login logic. Use cmdline if set, use AUTH_TOKEN next, finally user/pass from config file, then prompt.
    # figure out user
    if args["email"]:
        user_email = args["email"]
    elif CLOUDGENIX_USER:
        user_email = CLOUDGENIX_USER
    else:
        user_email = None

    # figure out password
    if args["pass"]:
        user_password = args["pass"]

    elif CLOUDGENIX_PASSWORD:
        user_password = CLOUDGENIX_PASSWORD
    else:
        user_password = None

    # check for token
    if CLOUDGENIX_AUTH_TOKEN and not args["email"] and not args["pass"]:
        cgx_session.interactive.use_token(CLOUDGENIX_AUTH_TOKEN)
        if cgx_session.tenant_id is None:
            print("AUTH_TOKEN login failure, please check token.")
            sys.exit()

    else:
        while cgx_session.tenant_id is None:
            cgx_session.interactive.login(user_email, user_password)
            # clear after one failed login, force relogin.
            if not cgx_session.tenant_id:
                user_email = None
                user_password = None

    ############################################################################
    # Iterate through tenant_ids and get machines, elements and sites
    ############################################################################
    curtime_str = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')

    ops = pd.DataFrame()

    resp = cgx_session.get.tenant_operators()
    if resp.cgx_status:
        operatorlist = resp.cgx_content.get("items",None)
        print("INFO: Num Operators: {} ".format(len(operatorlist)))
        print("INFO: Getting session data")

        for op in operatorlist:
            opdata = {}
            oid = op["id"]
            firstname = op.get("first_name", None)
            lastname = op.get("last_name", "-")
            email = op.get("email", None)

            opdata["first_name"] = firstname
            opdata["last_name"] = lastname
            opdata["email"] = email
            print("\t{}".format(op["email"]))
            resp = cgx_session.get.sessions_t(operator_id=oid)
            if resp.cgx_status:
                sessions = resp.cgx_content.get("items", None)
                timelist = {}
                for ses in sessions:
                    timelist[ses["_created_on_utc"]] = ses["type"]

                if len(timelist.keys()) > 0:
                    new = max(timelist.keys())
                    stype = timelist[new]

                else:
                    new = "No Record"
                    stype = "No Record"

            else:
                print("ERR: Could not retrieve Sessions info for user {}:{}:{}".format(firstname,lastname,email))
                new = "No Record"
                stype = "No Record"

            opdata["last_login"] = new
            opdata["session_type"] = stype
            ops = ops.append(opdata, ignore_index=True)

    else:
        print("ERR: Could not retrieve operators")
        cloudgenix.jd_detailed(resp)


    opsfile = "{}/operators_lastlogin_{}.csv".format(os.getcwd(), curtime_str)
    print("INFO: Saving data to file {}".format(opsfile))
    ops.to_csv(opsfile,index=False)

    #############################################################
    # Logout
    #############################################################

    cgx_session.get.logout()
    sys.exit()


if __name__ == "__main__":
    go()
