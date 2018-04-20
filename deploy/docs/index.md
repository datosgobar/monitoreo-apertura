# Monitoreo de Apertura - Deployment

Bienvenido a la documentación de "deployment" para Monitoreo de Apertura

## Consideraciones

### Primera conexión

Antes de usar el `playbook`, debemos agregar la clave pública de la máquina de deployment a todas las demas máquinas.
Ansible trabaja accediendo a cada una de ellas por SSH y la conexión SSH con contraseña debería estar desactivada.

Despues de agregar esas claves públicas, debemos conectarnos al menos una vez *desde la máquina de deployment*
para registrar las demás máquinas en el archivo `known_hosts`.

### Conceptos

En el archivo `hosts.sample` puede verse la estructura básica de un inventario.

Un host (e.i. "web0") representa *una máquina en la red*, la misma debe tener sus configuraciones únicas en un archivo `host_vars/<host>/vars.yml`.
Cabe destacar que, en este caso, "web0" *no es un nombre que se resuelva a una IP*, es simplemente un alias a una IP.
En el archivo "vars.yml" podemos configurar como se conecta a este server (IP, puerto, usuario, etc.).


## Requerimientos

- OS: `Ubuntu 16.04`
- SSH client
- Python 2.7.6
- Python virtualenv
- Python pip

Para instalar estos requerimientos podemos correr:

```bash
sudo apt install openssh-client python python-pip virtualenvwrapper -y
```
NOTA: Quizás sea necesario volver a entrar a la consola para que reconozca los comandos `mkvirtualenv` y `workon`

Luego creamos un nuevo "virtualenv" y lo activamos. Siempre que querramos correr el deploy, debemos usar activar el virtualenv.

```bash
mkvirtualenv -p $(which python) deploy
workon deploy # Activa el virtualenv
```

Luego deberíamos, si ya no lo hicimos, clonar el presente repositorio e instalamos la version de
ansible especificada en para el repositorio con el comando `pip install -r deploy/requirements.txt`


## Inicializacion por ambiente

- testing (TBD)
- staging (TBD)
- production (TBD)


## Actualización

Para actualizar un ambiente, debe correrse el playbook de nuevo.
Esto actualizará el repositorio automaticamente.


## Vagrant & Tests

Se puede probar con [vagrant](http://www.vagrantup.com/) siguiendo los siguientes pasos:

```bash
cd deploy/
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
vagrant up --no-provision
# Incluyo el archivo de Vault como ejemplo
ansible-playbook -i inventories/vagrant/hosts site.yml -v
```

Además con la variable de entorno "CHECKOUT_BRANCH" se puede configurar el branch que deseamos usar _dentro_ del servidor.

Para cambiar la cantidad de servidores de Elasticsearch debemos cambiar, dentro del archivo Vagranfile, la variable "ES_SERVER_COUNT" con un numero mayor a 1.
