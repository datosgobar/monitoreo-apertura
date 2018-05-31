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
