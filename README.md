## File Transfer

### Descripción
Aplicación de red de arquitectura cliente-servidor que implemente la funcionalidad de transferencia de archivos mediante las operaciones: UPLOAD (de un cliente hacia el servidor) y DOWNLOAD (del servidor hacia el cliente).


### ¿Cómo ejecutar?

Inicialización del servidor:

```console
$ python3 start-server.py -v
```

Carga por parte de un cliente de un archivo denominado `example.MOV` que se encuentra dentro de la carpeta local `resources`:

```console
$ python3 upload.py -n example.txt
```

Descarga de archivo denominado `example.MOV` que se encuentra dentro de la carpeta `files` del servidor:

```console
$ python3 download.py -n example.txt
```
