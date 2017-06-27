# Instrucciones de deploy

El script deployea automáticamente a través de ansible y git el proyecto de Django. Además configura el crontab para obtener indicadores una vez por día (a las 5 de la mañana).
### Requirements

- Ansible: `pip install -r requirements.txt`
- SSH client
  - Ubuntu: `apt-get install openssh-client`
  - Arch linux: `pacman -S openssh` ([docs](https://wiki.archlinux.org/index.php/Secure_Shell#OpenSSH))

### Deploy

El script acepta varias variables

    export REPO_URL=git@example.com/user:repo.git  # Repo a clonar (se necesita acceso, si es privado)
    export CHECKOUT_BRANCH=master  # branch o tag a clonar
    export POSTGRESQL_USER=database_user  # psql user name
    export POSTGRESQL_PASSWORD=database_password_xxxxxxx  # user password
    export HOST=8.8.8.8  # IP del server al que deployar
    export LOGIN_USER=root  # Usuario con acceso sudo del servidor

    bash deploy.sh -r $REPO_URL -p $POSTGRESQL_USER -P $POSTGRESQL_PASSWORD \
        -b $CHECKOUT_BRANCH -h $HOST -l $LOGIN_USER

Un ejemplo puede ser

    sh deploy.sh -r git@github.com:datosgobar/monitoreo-apertura.git -b master -p database_user -P database_password -h 181.209.63.95 -l llavandeira

### Update

Una vez deployado se puede actualizar el servidor usando `update.sh`:

    bash update.sh -r $REPO_URL -b $CHECKOUT_BRANCH -h $HOST -l $LOGIN_USER
