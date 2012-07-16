import random, math
import datetime, time
from Crypto.Cipher import AES
import base64
import mywish.settings
import httplib, urllib

def randomString(size, lowerCase):
    key = ''
    
    for i in range(size):
        ch = chr(int(math.floor(26 * random.random() + 65)));
        key += ch;
    
    if lowerCase:
        return key.lower()
    
    return key

def currnetTimeinMillisecond():
    current = datetime.datetime.utcnow()
    epoh = datetime()
    
def get_token(user):
    BLOCK_SIZE = 16 # Block-size for cipher (16, 24 or 32 for AES)
    #PADDING = '{' # block padding for AES
    
    # PKCS5 Padding
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
    unpad = lambda s : s[0:-ord(s[-1])]
    
    mode = AES.MODE_CBC
    encryptor = AES.new(mywish.settings.MWEncryptKey, mode, mywish.settings.MWEncryptIV)
    
    cookie = '%s|%s' %(user.email, int(time.time()*1000))
    encCookie = encryptor.encrypt(pad(cookie))
    base64Cookie = base64.urlsafe_b64encode(encCookie)
    
#    if base64Cookie.rindex('=') == base64Cookie.__len__() - 1:
#        s = list(base64Cookie)
#        s[base64Cookie.__len__()-1] = '1'
#        base64Cookie = "".join(s)
    
    return base64Cookie
    
