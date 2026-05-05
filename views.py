#!/usr/bin/env python3

import sys
import configparser
from vastpy import VASTClient
from ncsa_vast_common import *

import pprint

VAST_CREDENTIAL_FILE = 'vast_credentials.conf'

def parse_options( argv ):
    import argparse
    import textwrap
    parser = argparse.ArgumentParser(
           formatter_class = argparse.RawTextHelpFormatter,
           prog = 'views.py',
           description = textwrap.dedent('''\
                views.py

                This utility will display the views associated with the specified tenant.

           '''),

           epilog = textwrap.dedent('''\

                Chad Kerner, Staff Storage Engineer
                Storage Enabling Technologies
                National Center for Supercomputing Applications
                University of Illinois, Urbana-Champaign
                ckerner@illinois.edu      chad.kerner@gmail.com''')
           )

    parser.add_argument( "--creds",
                         dest = "credentials_file",
                         default = VAST_CREDENTIAL_FILE,
                         action = 'store',
                         help = "Credentials File. Default: %(default)s" )

    parser.add_argument( "--tenant", "-t",
                         dest = "tenant",
                         default = 'default',
                         action = 'store',
                         help = "Credentials File. Default: %(default)s" )

    parser.add_argument( "--debug",
                         dest = "debug",
                         default = False,
                         action = 'store_true',
                         help = "Execute in debug mode. This is pretty verbose. Default: %(default)s")

    options, args = parser.parse_known_args( argv )
    return ( options, args )


if __name__ == '__main__':
   ( options, args ) = parse_options( sys.argv[1:] )

   try:
      vast_creds = load_vast_credentials( options.credentials_file, options.tenant )
   except Exception as e:
      print( f"Tenant: {options.tenant} not found in the credentials file: {options.credentials_file}" )
      sys.exit(100)

   if options.debug:
      print( f"VMS: {vast_creds['vms']}" )
      print( f"User: {vast_creds['user']}" )
      print( f"Password: {vast_creds['password']}" )
      print( f"Tenant: {vast_creds['tenant']}" )

   V = VASTClient(user=vast_creds['user'],password=vast_creds['password'],address=vast_creds['vms'],tenant=vast_creds['tenant'])

   views = V.views.get()

   if views:
      print(f"{'Tenant':6}  {'Id':2} {'View Name':<40} {'Physical':>10} {'Logical':>10}  {'DEDUP':>5}")
      for v in views:
          if int(v['logical_capacity']) > 0:
             pct = ( v['logical_capacity'] / v['physical_capacity'] ) 
          else:
             pct = 0
          print(f"{v['tenant_id']:>6}  {v['id']:>2} {v['title']:<40} {human_readable(v['physical_capacity']):>10} "
                f"{human_readable(v['logical_capacity']):>10}  {pct:5.2f}")
   else:
      print(f"No Views For Tenant: {options.tenant}")

