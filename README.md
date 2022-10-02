## File Transfer

Aplicación de red de arquitectura cliente-servidor que implemente la funcionalidad de transferencia de archivos mediante las operaciones: UPLOAD (de un cliente hacia el servidor) y DOWNLOAD (del servidor hacia el cliente).


### ¿Cómo ejecutar?

Inicialización del servidor:

```console
$ python3 start-server.py -v
```

Carga por parte de un cliente de un archivo denominado `example.MOV` que existe dentro de la carpeta local `resources`:

```console
$ python3 upload.py -n example.MOV
```

Descarga de archivo denominado `example.MOV` que se encuentra dentro de la carpeta `files` del servidor:

```console
$ python3 download.py -n example.MOV
```

# tp1-intro

## Errors to check
- Upload.py:
  - Sometimes receiving a None from the client, therefore, it can't unpack it
```shell
ERROR:root:An error occurred when sending file to server: cannot unpack non-iterable NoneType object
DEBUG:root:Socket <socket.socket [closed] fd=-1, family=AddressFamily.AF_INET, type=SocketKind.SOCK_DGRAM, proto=0> closed
```

