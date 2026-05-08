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
           prog = 'list_support_bundles.py',
           description = textwrap.dedent('''\
                list_support_bundles.py

                This utility will list all of the created support bundles.

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

    parser.add_argument( "--verbose", "-v",
                         dest = "verbose",
                         default = False,
                         action = 'store_true',
                         help = "Execute in verbose mode. This is VERY verbose. Default: %(default)s")

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
      vast_creds = load_vast_credentials( options.credentials_file, 'default' )
   except Exception as e:
      print( f"Tenant: {options.tenant} not found in the credentials file: {options.credentials_file}" )
      sys.exit(100)

   V = VASTClient(user=vast_creds['user'],password=vast_creds['password'],address=vast_creds['vms'],tenant=vast_creds['tenant'])

   bundles = V.supportbundles.get()

   if bundles:
      if options.verbose == False:
         print( f"{'Id':>3}  {'Timestamp':19}  {'Bundle Filename':70}  {'Bundle Size':>15}" )
      for bundle in  bundles:
          if options.verbose:
             pprint.pprint( bundle )
          else:
             print( f"{bundle['id']:3}  {bundle['create_datetime']:19}  {bundle['bundle_file']:70}  {human_readable(bundle['bundle_size']):>15}" )
   else:
      print(f"There are no support bundles on the system.")


