# File Transfer

Aplicación de red de arquitectura cliente-servidor que implemente la funcionalidad de transferencia de archivos mediante las operaciones: _UPLOAD_ (de un cliente hacia el servidor) y _DOWNLOAD_ (del servidor hacia el cliente).

### Requerimientos

El único requerimiento es Python. En caso de no poseerlo, seguir las instrucciones de https://www.python.org/downloads/ para instalarlo.

## Inicialización del servidor

Lo primero que debe hacerse es iniciar el servidor, para lo cual se debe ejecutar el siguiente comando y utilizar múltiples flags:

```console
$ python 3 start-server.py [-h] [-v | -q] [-H ADDR] [-p PORT] [-s DIRPATH]
```

Opcionales:

`-h`, `--help`: otorga información sobre las distintas formas de ejecución del comando y salida.

`-v`, `--verbose`: incrementa la _verbosidad_ del output.

`-q`, `--quiet`: decrementa la _verbosidad_ del output.

`-H`, `--host`: permite indicar la dirección IP del servidor.

`-p`, `--port`: permite indicar el puerto del servidor.

`-s`, `--storage`: permite indicar el path de almacenamiento.

## Cliente

Tras haber inicializado, el servidor ya está listo para recibir requests. Simplemente abriendo una nueva consola un usuario puede cargar un archivo o descargarlo.

### Carga

Para realizar una carga (_UPLOAD_) de un archivo, éste debe haberse almacenado previamente en la carpeta _resources_ y luego simplemente debe procederse a utilizar el siguiente comando, con los flags que se elijan.

```console
$ python3 upload.py [-h] [-v | -q] [-H ADDR] [-p PORT] [-s FILEPATH] [-n FILENAME]
```

Opcionales: mismos flags que el comando `start-server` y los agregados a continuación.

`-s`, `--src`: permite indicar el path del archivo a cargar.

`-n`, `--name`: permite indicar el nombre con que se cargará el archivo en el servidor.

`--snw`: permite elegir Stop & Wait como protocolo de carga (es el default para la carga).

`--gbn`: permite elegir Go-BACK-N como protocolo de carga.

Importante:
- Las cargas se preservarán en la carpeta `files`.
- Los flags `--snw` y `--gbn` son mutuamente excluyentes, tanto en la carga como en la descarga.

### Descarga

Tras haber realizado cargas de archivos, el usuario ya puede realizar descargas de los archivos que posea el servidor, las cuales aparecerán en la carpeta `downloads` que en caso de no poseerse, se creará automáticamente tras la request de descarga.

```console
$ python3 download.py [-h] [-v | -q] [-H ADDR] [-p PORT] [-d FILEPATH] [-n FILENAME]
```

Opcionales: mismos flags que el comando `start-server` y los agregados a continuación.

`-d`, `--dst`: permite indicar el path dónde almacenar el archivo a descargar.

`-n`, `--name`: permite indicar el nombre del archivo a descargar.

`--snw`: permite elegir Stop & Wait como protocolo de descarga.

`--gbn`: permite elegir Go-BACK-N como protocolo de descarga (es el default para la descarga).
