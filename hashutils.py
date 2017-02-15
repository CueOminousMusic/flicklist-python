import random, string, hashlib, hmac

def make_salt():
    return ''.join(random.choice(string.letters) for x in range(5))


def make_pw_hash(name, pw,salt=None):
    if salt is None:
        salt = make_salt()

    h = hashlib.sha256(name + pw + salt).hexdigest()

    return '%s,%s' % (h, salt)


def valid_pw(name, pw, h):
    salt = h.split(',')[1]
    return h == make_pw_hash(name, pw, salt)


SECRET = 'sauce'

def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return '%s|%s' % (s, hash_str(s))

def check_secure_val(unknown_val):
    s = unknown_val.split('|')[0]
    if unknown_val == make_secure_val(s):
        return s
