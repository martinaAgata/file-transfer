def encode(type, message = ""):
    if message != "":
        data = f"{type} {message}"
    else:
        data = type
    return data.encode()