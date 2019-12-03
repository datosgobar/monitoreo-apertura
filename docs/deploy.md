# Configuración de deploy automático

El repositorio del proyecto cuenta con una integración con [Travis-CI](http://travis-ci.org/datosgobar/) para realizar deploys automáticos a varios servidores:

* Se actualiza la instancia de desarrollo (_testing_, o _dev_) en cada push a master.
* Se actualiza la instancia de staging en cada creación de un tag, o lo que es equivalente, un Release de GitHub.

En este documento se informa en detalle el funcionamiento de esta automatización, y cómo configurarla de cero.

## Scripts

El script principal y punto de entrada del deploy es `scripts/deploy/run_deploy.sh`. Internamente se divide en otros tres:

* `variables.sh`: Lee de travis las variables de entorno necesarias para el resto del script. 
* `prepare.sh`: Realiza tareas previas a la acción de deploy en sí, como levantar VPNs y agregar claves de SSH para poder entrar al servidor
* `deploy.sh`: Ejecuta el deploy en sí: se conecta por SSH a la máquina y corre un script ya preparado en la máquina para configurar el servidor con la última versión

El script decide qué ambiente deployar según cómo se ejecuta. El primer parámetro de `run_deploy.sh` es el ambiente. Entonces, para deployar a testing, se ejecuta `./scripts/deploy/run_deploy.sh testing`, y para staging, `./scripts/deploy/run_deploy.sh staging`. En `travis.yml` tenemos configuradas las reglas para ejecutar estos scripts así en push a master y on tag:

```yaml
deploy:
  - skip_cleanup: true
    provider: script
    script: scripts/deploy/run_deploy.sh testing
    on:
      branch: master  # <-- sólo en pushes a master
  - skip_cleanup: true
    provider: script
    script: scripts/deploy/run_deploy.sh staging
    on:
      tags: true  # <-- sólo en pushes de tags
```

## Variables

En `variables.sh` se leen todas las variables configuradas en Travis. Al tener dos ambientes a los que deployar, se tienen que definir las variables para ambos ambientes, y en el momento de correr el script de deploy, usar uno de los dos grupos. Si es un push a master, se leen las de testing, si es un tag, se leen las de staging. 

A continuación se listan algunas variables a modo de ejemplo. Estas variables **se cargan todas en travis**, en la URL `https://travis-ci.org/datosgobar/<nombre del repo>/settings`. Las variables siguientes son para el ambiente de desarrollo, similarmente existen variables idénticas para staging

* `$TESTING_USE_VPN`: Setear a cualquier valor si tenemos que configurar una VPN para acceder al servidor (en la sección de Prepare se explica cómo meter las credenciales)
* `$TESTING_DEPLOY_TARGET_IP`
* `$TESTING_DEPLOY_TARGET_SSH_PORT`
* `$TESTING_DEPLOY_TARGET_USERNAME`
* `$TESTING_DEPLOY_VAULT_PASS_FILE`: Contraseña del vault de Ansible usado para el script de deploy (si aplica)

Similarmente existen variables equivalentes para el ambiente de staging: 

* `$STAGING_USE_VPN`
* `$STAGING_DEPLOY_TARGET_IP`
* `$STAGING_DEPLOY_TARGET_SSH_PORT`
* `$STAGING_DEPLOY_TARGET_USERNAME`
* `$STAGING_DEPLOY_VAULT_PASS_FILE`

Estas variables, según el ambiente a deployar, son leídas y pasadas a nombres genéricos a usarse en los pasos siguientes.

## Prepare

En este paso se levantan las credenciales para poder acceder al servidor. Son dos pasos: configurar la VPN, y configurar el cliente de SSH para estar autorizados a ingresar. Estos archivos se encuentran **pusheados en el repo, encriptados**. El archivo `scripts/deploy/files.tar.gz.enc` se desencripta y se extraen los archivos. Internamente, el directorio comprimido tiene la siguiente estructura: 

```
files/
├── staging
│   ├── build@travis-ci.org
│   └── client.ovpn
└── testing
    ├── build@travis-ci.org
    └── client.ovpn
```

La key (privada) de ssh de cada ambiente se guarda con el nombre `build@travis-ci.org`, y las credenciales de VPN con `client.ovpn`. Inicialmente, debemos armar este directorio, encriptarlo con la utilidad CLI de Travis, y pushearlo al repo, con la ruta dada, `scripts/deploy/files.tar.gz.enc`. Nosotros estamos en el caso de "Encyrpting multiple files". ([link](https://docs.travis-ci.com/user/encrypting-files/)). Una vez hecho el paso de encriptación, debemos obtener las variables de entorno `$*_key`, `$*_iv`, y configurarlas en las líneas del script de `prepare.sh`. Las variables a setear **son el nombre de las variables de encriptación**, y no los valores. Ver el ejemplo:

```
# prepare.sh, línea 9-10. Reemplazar con el nombre de variables dadas por travis al haber hecho la encriptación

export files_key_var_name="encrypted_fd34314b9fa6_key"
export files_iv_var_name="encrypted_fd34314b9fa6_iv"
```

## Deploy

Una vez configuradas las variables y el directorio encriptado, sólo resta realizar el deploy. El script `deploy.sh` agrega la clave de ssh al usuario actual, y ejecuta comandos a través de ssh. Actualmente está configurado para:

* Hacer un pull del repo
* Ejecutar el script de deploy de ansible dentro del repo, pasando la variable `$*_VAULT_PASS_FILE` como contraseña de vault.

Este script puede ser modificado con cualquier acción que querramos realizar dentro de la máquina. Se recomienda dejar preparado un script de bash para simplificar la ejecución desde travis, y poder reproducir las acciones que se realizan, en caso de querer hacer un deploy manual sin pasar por el paso de integración continua.