# Testing

_Ultima actualizacion: 19/03/2018_

## Pre-requisitos

Antes de correr `ansible-playbook` para usar el deploy, es necesario tener los servidores configurados.

En esta documentacion se asume la presencia de un unico servidor

### Configuracion general

Los servidores deben cumplir con los siguientes puntos:

Nota: para el servidor de "deploy", el usuario no es necesario que sea "sudoer"

- Conocer los usuarios con los que nos conectaremos.
- Conocer las contraseñas de los usuarios.
- Que los usuarios sean "sudoers".
- Servidor SSH levantado.
- Servidor SSH configurado para no aceptar conexiones con contraseña.

### Acceso desde maquina de deployment

La maquina de "deploy" debe poder acceder al resto de las maquinas mediante `ssh` sin necesidad de introducir una contraseña.
Para esto generamos, en la maquina de "deploy" y con el usuario de deployment, generamos un par de clave publica/privada con el siguiente comando:

Nota: No escribir ninguna "secure passphrase" ya que no seremos capaces de escribirla cuando se requiera.

```
ssh-keygen -t rsa -b 4096 -C "deploy-dev@apimgt-deploy-deploy01"
```

Luego agregamos la clave publica (`~/.ssh/id_rsa.pub`) al archivo `authorized_keys` de los otros servidores.

### Obtener codigo de la aplicacion

Para lograr obtener el codigo de la aplicacion, que sera clonando el repositorio de Github,
debemos agregar la clave publica del servidor a las "Deploy Keys" del repositorio.

Luego, en el servidor "deploy" y con el usuario de deployment, creamos el directorio "dev" y clonamos el repositorio:

```
mkdir ~/dev && cd ~/dev
git clone git@github.com:datosgobar/monitoreo-apertura.git
cd ~/dev/monitoreo-apertura/deploy
```

### Configuracion & setup inicial

Para este paso necesitamos tener instalado Python3 y Python3-virtualenv.
En Ubuntu 16.04:

```
sudo apt update
sudo apt install python3 python3-venv python3-dev libssl-dev -y
```

Luego, es necesario instalar los requerimientos en un virtualenv.
Para crear el virtualenv corremos:

```
cd ~/dev
python3 -m venv ./venv
```

Luego activamos el "virtualev" e instalamos los requerimientos para el deployment.

```
cd ~/dev/
. ./venv/bin/activate
cd monitoreo-apertura/deploy/
pip install -r requirements.txt
```

Despues de esto, deberiamos tener el binario `ansible` disponible.

## Configurar el inventario de ansible

Antes de correr el deployment, debemos configurar los servidores.
Si miramos el archivo `inventories/hosts.sample` veremos la version mas actualizada de la arquitectura.


```
web0

[web]
web0

[rqworkers]
web0

[api_cluster:children]
web

```


Este archivo debemos copiarlo y pegarlo en la subcarpeta que queremos, en el caso del ambiente de testing, seria:

```
ENVIRONMENT="testing"
cd ~/dev/monitoreo-apertura/deploy
mkdir "inventories/$ENVIRONMENT"
cp inventories/hosts.sample "inventories/$ENVIRONMENT/hosts"

```


### Configuracion especifica de cada host

En esta documentacion, asumiremos que tenemos los siguientes servidores e IPs:

web0: 192.168.65.1


Luego debemos configurar cada uno de los "hosts" definidos en ese archivo.

Para eso crearemos los directorios `group_vars/` y `host_vars/` _por fuera_ del directorio de la aplicacion:

```
mkir ~/dev/config/
cd ~/dev/config/
mkdir group_vars/ host_vars/

```

Luego agregaramos la configuracion para cada server con los siguientes archivos.

**host_vars/web0/vars.yml**

En este archivo podremos poner configuracion especifica del servidor "web".
Como se puede ver, sera el host a conectar, el puerto y con que usuario.

```yaml
---

ansible_host: "{{ vault_ansible_host }}"
ansible_port: "{{ vault_ansible_port }}"
ansible_user: "{{ vault_ansible_user }}"

```


**host_vars/web0/vault.yml**

En este archivo pondremos valores que podremos referencias, pero que terminaran siendo encriptados.
En el paso final se muestra como.

```yaml
---

# La ip real a donde conectarse desde el servidor de "deploy"
vault_ansible_host: 192.168.1.1
vault_ansible_port: 22
# El usuario real con el cual conectarse
vault_ansible_user: mi_usuario
# La contraseña con la cual poder correr comandos con "sudo"
ansible_become_pass: secure_pass
```

### Configuracion de grupos

Hasta el momento, el unico grupo es el definido como `web`
En este grupo pondremos las variables que no son especificas al host.

**group_vars/web/vars.yml**


```yaml
---

# psql

postgresql_user: {{ vault_postgresql_user }}
postgresql_password: {{ vault_postgresql_password }}
postgresql_readonly_user: {{ vault_postgresql_readonly_user }}
postgresql_readonly_password: {{ vault_postgresql_readonly_password }}

# Django
application_name: monitoreo-testing
checkout_branch: master

```


**host_vars/web0/vault.yml**

En este archivo pondremos valores que podremos referencias, pero que terminaran siendo encriptados.
En el paso final se muestra como.

```yaml
---

vault_postgresql_user: database_user
vault_postgresql_password: database_pass
vault_postgresql_readonly_user: readonly_database_user
vault_postgresql_readonly_password: readonly_database_pass
```


### Encriptacion de los archivos

Hasta ahora hemos escrito as credenciales en archivos de texto plano.
Para aumentar la seguridad los encriptaremos. Para eso debemos generar una clave propia que usaremos
en conjunto con `ansible-vault`.

Luego de que hemos generado la clave, corremos el comando:

```bash
cd ~/dev/config

ansible-vault encrypt host_vars/web0/vault.yml \
                group_vars/web/vault.yml
```

Este comando nos pedira una clave, la cual sera la que acabamos de generar.


### Crear los links de los archivos

Finalmente creamos los links:

```bash

cd ~/dev/config

ln -s $PWD/group_vars ~/dev/monitoreo-apertura/deploy/inventories/testing/group_vars
ln -s $PWD/host_vars ~/dev/monitoreo-apertura/deploy/inventories/testing/host_vars
```


## Pasos finales

Antes de correr el deployment completo, debemos configurar el servidor "web" para
que pueda clonar el proyecto. Esto se hara con un usuario "devartis" (default) que
no existe si aun no hemos corrido el deployment. Entonces, corramos parte del "playbook"
que nos crea este usuario:

```bash
. ~/dev/venv/bin/activate
cd ~/dev/monitoreo-apertura/deploy

ansible-playbook api_cluster.yml -i inventories/testing/hosts --ask-vault-pass
```

Este comando correra algunas tareas de configuracion y creara los usuarios en todos los servidores.
Tambien nos servira de prueba para ver si ansible puede conectarse y correr comandos en todos los servidores.
Antes de empezar a correr cualquier comando, `ansible-playbook` nos pedira la clave que usamos para encriptar
los archivos con `ansible-vault`.
Si todo va bien, deberiamos ver algo como (los valores de "changed" y "ok" pueden variar):

```
PLAY RECAP ***********************************************************************************************************************************************************************************
kong0                      : ok=18   changed=2    unreachable=0    failed=0
psql-redis0                : ok=18   changed=2    unreachable=0    failed=0
web0                       : ok=18   changed=2    unreachable=0    failed=0
```


Una vez asegurado, entramos al servidor que definimos como "web1" y nos logueamos como el usuario "devartis".
Correr estos comandos desde el serveridor de deploy:

```
@deploy-server$ ssh mi_user@192.168.65.1

# Una vez logueados, cambiamos de usuario
mi_user@web-server$ sudo su - devartis

devartis@web-server$ cat .ssh/id_rsa.pub
```

La clave publica que veremos debe ser copiada a las "deploy keys" del repositorio en Github.


## Deployment

Una vez configurada la key, podemos volver al servidor de deployment y correr todo el "playbook":

```

ansible-playbook site.yml -i inventories/testing/hosts --ask-vault-pass
```

Si es la primera vez que corremos este comando, puede llegar a tardar bastante, ya que tendra que instalar y configurar la aplicacion
por primera vez.

