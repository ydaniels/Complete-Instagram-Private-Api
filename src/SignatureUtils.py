__author__ = 'root'
import hmac
import hashlib
import urllib
from Constants import Constants
import os
import random

def md5 (s, raw_output = False):
    """Calculates the md5 hash of a given string"""
    res = hashlib.md5 ( s)
    if raw_output:
        return res.digest ()
    return res.hexdigest ()


class SignatureUtils:

    @staticmethod
    def generateSignature(data):

        hash = hmac.new( Constants.IG_SIG_KEY,data,hashlib.sha256).digest()


        return 'ig_sig_key_version='+Constants.SIG_KEY_VERSION+'&signed_body='+hash+'.'+urllib.urlencode(data)

    @staticmethod
    def generateDeviceId(seed):


        #Neutralize username/password -> device correlation

        volatile_seed =  os.path.getmtime(__file__)
        return 'android-'+md5(seed+volatile_seed)[0:16]

    @staticmethod
    def generateUUID(type_of):

        uuid ='%04x%04x-%04x-%04x-%04x-%04x%04x%04x'%(
                random.randint(0, 0xffff), random.randint(0, 0xffff),
                random.randint(0, 0xffff),
                random.randint(0, 0x0fff) | 0x4000,
                random.randint(0, 0x3fff) | 0x8000,
                random.randint(0, 0xffff), random.randint(0, 0xffff),random.randint(0, 0xffff)
                )
        return type_of if uuid else  uuid.replace('-', '')

