# Instrucciones de deploy

El script deployea automáticamente a través de ansible y git el proyecto de Django. Además configura el crontab para obtener indicadores una vez por día (a las 5 de la mañana).
### Requerimientos

- Ansible: `pip install -r requirements.txt`
- SSH client
  - Ubuntu: `apt-get install openssh-client`
  - Arch linux: `pacman -S openssh` ([docs](https://wiki.archlinux.org/index.php/Secure_Shell#OpenSSH))

### Deploy

Se debe ejecutar el script de deploy, y además generar y subir manualmente las credenciales de google drive.

El deploy ocurre en dos pasos. Primero ejecutar el script en este directorio, `deploy.sh`. Luego, es necesario agregar dos archivos, credenciales de google drive, para calcular los indicadores de la planilla del PAD.

Finalmente es necesario ejecutar el cálculo de indicadores manualmente por primera vez y crear un usuario administrador del panel de control de la aplicación web.

#### Ejecución del script

El script acepta varias variables. Tener en cuenta que el usuario y contraseña de postgres es del usuario _a crear_, y no un usuario previamente creado.

    export REPO_URL=git@example.com/user:repo.git  # Repo a clonar (se necesita acceso, si es privado)
    export CHECKOUT_BRANCH=master  # branch o tag a clonar
    export POSTGRESQL_USER=database_user  # psql user name
    export POSTGRESQL_PASSWORD=database_password_xxxxxxx  # user password
    export HOST=8.8.8.8  # IP del server al que deployar
    export LOGIN_USER=root  # Usuario con acceso sudo del servidor

    bash deploy.sh -r $REPO_URL -p $POSTGRESQL_USER -P $POSTGRESQL_PASSWORD \
        -b $CHECKOUT_BRANCH -h $HOST -l $LOGIN_USER

El resultado de esta ejecución es la creación de un nuevo usuario en HOST, `datosgobar`, y la configuración del stack entero para correr la aplicación, en `/home/datosgobar/webapp/`
Un ejemplo puede ser

    sh deploy.sh -r git@github.com:datosgobar/monitoreo-apertura.git -b master -p database_user -P database_password -h 181.209.63.95 -l llavandeira

#### Creación de credenciales de Google Sheets

La generación de credenciales para la lectura de planillas de Google Spreadsheets se lleva a cabo en dos pasos, en un entorno local:
- Generar credenciales del proyecto como indica el paso 1 de [esta guía](https://developers.google.com/sheets/api/quickstart/python). Esta tarea la debe realizar un usuario de Google con acceso a la planilla de indicadores.
- Ejecutar `python google_drive.py`, en el directorio `app/indicadores_pad` del proyecto, y seguir las instrucciones para generar las credenciales del proyecto. Para ello deben ser seteadas la variable de entorno `GOOGLE_DRIVE_PROJECT_CREDENTIALS` a la ruta absoluta al archivo generado en el paso anterior. Como resultado se obtendrá el archivo `user_credentials.json`.

Estos archivos luego deberán ser copiados manualmente (por `sftp`) al directorio `config/app` del proyecto deployado, con los nombres `client_secret.json` y `user_credentials.json` respectivamente.

Estos archivos deben poder ser leídos por el usuario bajo el cual corre la tarea programada de cálculo de indicadores.

#### Ejecución del cálculo de indicadores

Por último es necesario ejecutar el primer cálculo de indicadores manualmente. Correr (como el usuario creado por el script de deploy, `datosgobar`) `run_indicadores.sh` (ya ubicado en `/usr/local/bin`) sin argumentos. 

#### Creación del usuario administrador del panel de control de la web

Para crear un usuario administrador del panel de administración de la aplicación es necesario ejecutar el siguiente comando desde una consola del servidor:

```bash
. /home/datosgobar/webapp/.venv/bin/activate
cd /home/datosgobar/webapp/app
python manage.py createsuperuser --settings=conf.settings.production  # Usar los settings correspondientes al ambiente (ver #14)
```

El script pedirá los siguientes datos:

* Nombre de usuario (alfanumérico)
* Dirección de correo electrónico (opcional)
* Contraseña (alfanumérica)

Con las credenciales provistas, se podrá ingresar al panel de administración de la aplicación.

### Update

Una vez deployado se puede actualizar el servidor usando `update.sh`:

    bash update.sh -r $REPO_URL -b $CHECKOUT_BRANCH -h $HOST -l $LOGIN_USER
