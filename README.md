# tp1-intro

## Errors to check
- Upload.py:
  - Sometimes receiving a None from the client, therefore, it can't unpack it
```shell
ERROR:root:An error occurred when sending file to server: cannot unpack non-iterable NoneType object
DEBUG:root:Socket <socket.socket [closed] fd=-1, family=AddressFamily.AF_INET, type=SocketKind.SOCK_DGRAM, proto=0> closed
```
    