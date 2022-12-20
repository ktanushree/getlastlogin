# getlastlogin
Script to retrieve last login time for all Prisma SDWAN Operators

#### Synopsis
This script retrieves all operators configured on Prisma SDWAN. It then retrieves operators sessions for each operator and determines the user's last login time.

#### Requirements
* Active Prisma SDWAN Account
* Python >=3.6
* Python modules:
    * CloudGenix Python SDK >= 6.0.1b1 - <https://github.com/CloudGenix/sdk-python>

#### License
MIT

#### Installation:
 - **Github:** Download files to a local directory, manually run `getlastlogin.py`. 

### Examples of usage:
Get events from a site (past 3 hours):
```
./getlastlogin.py 
```

Help Text:
```angular2
(base) Tanushree:cprod_data tkamath$ ./getlastlogin.py -h
usage: getlastlogin.py [-h] [--controller CONTROLLER] [--insecure] [--email EMAIL] [--pass PASS] [--debug DEBUG]

Prisma SDWAN: Operators Last Login.

optional arguments:
  -h, --help            show this help message and exit

API:
  These options change how this program connects to the API.

  --controller CONTROLLER, -C CONTROLLER
                        Controller URI, ex. C-Prod: https://api.cloudgenix.com
  --insecure, -I        Disable SSL certificate and hostname verification

Login:
  These options allow skipping of interactive login

  --email EMAIL, -E EMAIL
                        Use this email as User Name instead of prompting
  --pass PASS, -PW PASS
                        Use this Password instead of prompting

Debug:
  These options enable debugging output

  --debug DEBUG, -D DEBUG
                        Verbose Debug info, levels 0-2
(base) Tanushree:cprod_data tkamath$ 
```

#### Version
| Version | Build | Changes |
| ------- | ----- | ------- |
| **1.0.0** | **b1** | Initial Release. |


#### For more info
 * Get help and additional Prisma SDWAN Documentation at <https://docs.paloaltonetworks.com/prisma/prisma-sd-wan>
 
