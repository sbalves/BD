def encode(obj):
    return hash(obj)


password_hash = encode("pato345")
print("pass codificada: " + str(password_hash))


def verify_password(user_pass):
    return hash(user_pass) == password_hash


"""
def decode(value):
    return # Como eu decodificaria aqui ?

password_hash = encode("pato345")
password = decode(password_hash)
"""
