#!/usr/bin/env python3

import sys
import configparser
from vastpy import VASTClient
from ncsa_vast_common import *
import pycurl
import time
import os
import pprint

VAST_CREDENTIAL_FILE = 'vast_credentials.conf'

def parse_options( argv ):
    import argparse
    import textwrap
    parser = argparse.ArgumentParser(
           formatter_class = argparse.RawTextHelpFormatter,
           prog = 'download_support_bundle.py',
           description = textwrap.dedent('''\
                download_support_bundle.py

                This utility will download the specified support bundle.

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

    parser.add_argument( "--id",
                         dest = "bundle_id",
                         default = None,
                         action = 'store',
                         help = "Bundle File Id. Default: %(default)s" )

    parser.add_argument( "--verbose", "-v",
                         dest = "verbose",
                         default = False,
                         action = 'store_true',
                         help = "Execute in verbose mode. Default: %(default)s")

    parser.add_argument( "--debug",
                         dest = "debug",
                         default = False,
                         action = 'store_true',
                         help = "Execute in debug mode. This is pretty verbose. Default: %(default)s")

    options, args = parser.parse_known_args( argv )
    return ( options, args )


if __name__ == '__main__':
   ( options, args ) = parse_options( sys.argv[1:] )

   if not options.bundle_id:
      print( "No bundle id has been specified." )
      sys.exit( 100 )

   try:
      vast_creds = load_vast_credentials( options.credentials_file, 'default' )
   except Exception as e:
      print( f"Tenant: {options.tenant} not found in the credentials file: {options.credentials_file}" )
      sys.exit(100)

   V = VASTClient(user=vast_creds['user'],password=vast_creds['password'],address=vast_creds['vms'],tenant=vast_creds['tenant'])

   bundle_info = V.supportbundles.get( id=int( options.bundle_id ) )[0]

   if options.debug:
      pprint.pprint( bundle_info )

   bundle_name = bundle_info['bundle_file']
   bundle_size = bundle_info['bundle_size']
   bundle_url = bundle_info['bundle_url']

   print( f"Downloading Bundle Id: {options.bundle_id} - {bundle_name}" )

   max_tries = 10
   attempt = 0
   while attempt < max_tries:
      if bundle_name:
         try:
            if os.path.exists( bundle_name ):
               os.remove( bundle_name )

            with open( bundle_name, 'wb' ) as f:
               def progress_callback(download_t, downloaded_now, upload_t, upload_now):
                   if download_t > 0:
                      percent = (downloaded_now / download_t) * 100
                      print(f"\rProgress: {percent:.1f}%", end='', flush=True)

               c = pycurl.Curl()
               c.setopt( c.URL, bundle_url )
               c.setopt( c.WRITEDATA, f )
               c.setopt(c.FOLLOWLOCATION, True)
               c.setopt(c.SSL_VERIFYPEER, False)  # Disable peer certificate verification
               c.setopt(c.SSL_VERIFYHOST, 0)      # Disable hostname verification
               if options.verbose:
                  c.setopt(c.NOPROGRESS, False)
                  c.setopt(c.XFERINFOFUNCTION, progress_callback)
               c.setopt(c.CONNECTTIMEOUT, 30)
               c.setopt(c.TIMEOUT, 300)

               c.perform()

               http_code = c.getinfo( pycurl.HTTP_CODE )
               c.close()

               print()

               if http_code == 200:
                  print( f"Download successful: {bundle_name}     {bundle_size} Bytes" )
                  sys.exit(0)
               else:
                  raise pycurl.error( f"HTTP Error Code: {http_code}" )

         except pycurl.error as e:
            attempt += 1
            print()
            if attempt < max_tries:
               print(f"Error downloading file (attempt {attempt}/{max_tries}): {e}" )
            else:
               print( f"Download Failed" )
               sys.exit(1)




