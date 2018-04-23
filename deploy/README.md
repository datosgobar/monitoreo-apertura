# Instrucciones de deploy

El script deployea automáticamente a través de ansible y git el proyecto de Django. Además configura el crontab para obtener indicadores una vez por día (a las 5 de la mañana).

## Requerimientos

- Ansible y librerías de credenciales de google: `pip install -r requirements.txt`
- SSH client
  - Ubuntu: `apt-get install openssh-client`
  - Arch linux: `pacman -S openssh` ([docs](https://wiki.archlinux.org/index.php/Secure_Shell#OpenSSH))

## Deploy

Se debe ejecutar el script de deploy, y además generar y subir manualmente las credenciales de google drive.

Primero debemos seguir las [instrucciones de deployment](docs/index.md).

Luego, es necesario agregar dos archivos, credenciales de google drive, para calcular los indicadores de la planilla del PAD.

Finalmente es necesario ejecutar el cálculo de indicadores manualmente por primera vez y crear un usuario administrador del panel de control de la aplicación web.

### Creación de credenciales de Google Sheets

La generación de credenciales para la lectura de planillas de Google Spreadsheets se lleva a cabo en dos pasos, en un entorno local:

- Generar credenciales del proyecto como indica el paso 1 de [esta guía](https://developers.google.com/sheets/api/quickstart/python). Esta tarea la debe realizar un usuario de Google con acceso a la planilla de indicadores.
- Ejecutar `python google_drive.py`, en el directorio `app/indicadores_pad` del proyecto, y seguir las instrucciones para generar las credenciales de usuario. Para ello deben ser seteadas la variable de entorno `GOOGLE_DRIVE_PROJECT_CREDENTIALS` a la ruta absoluta al archivo generado en el paso anterior. Como resultado se obtendrá el archivo `user_credentials.json`.

Estos archivos luego deberán ser copiados manualmente (por `sftp`) al directorio `config/app` del proyecto deployado, con los nombres `client_secret.json` y `user_credentials.json` respectivamente.

Estos archivos deben poder ser leídos por el usuario bajo el cual corre la tarea programada de cálculo de indicadores.

### Ejecución del cálculo de indicadores

Por último es necesario ejecutar el primer cálculo de indicadores manualmente. Correr (como el usuario creado por el script de deploy, `datosgobar`) `run_indicadores.sh` (ya ubicado en `/usr/local/bin`) sin argumentos.

### Creación del usuario administrador del panel de control de la web

Para crear un usuario administrador del panel de administración de la aplicación es necesario ejecutar el siguiente comando desde una consola del servidor:

```bash
. /home/datosgobar/webapp/.venv/bin/activate
cd /home/datosgobar/webapp/app
python manage.py createsuperuser --settings=conf.settings.production  # Usar los settings correspondientes al ambiente (ver #14)
```

El script pedirá los siguientes datos:

- Nombre de usuario (alfanumérico)
- Dirección de correo electrónico (opcional)
- Contraseña (alfanumérica)

Con las credenciales provistas, se podrá ingresar al panel de administración de la aplicación.

## Update

Simplemente volver a correr el script de deployment.
