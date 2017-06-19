# crear entorno virtual e instalar paquetes
# remover entorno virtual
# crear cronfile
# instalar cronfile
# correr rutina diaria

# Las dos recetas siguientes fueron tomadas de
# http://blog.bottlepy.org/2012/07/16/virtualenv-and-makefiles.html
venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || virtualenv venv
	venv/bin/pip install -r requirements/base.txt
	touch venv/bin/activate

# Las siguientes recetas son especÃficas a nuestro repositorio
install_cron: cron_jobs
	@echo "ROOTDIR=$$PWD" >> .cronfile
	@echo "PYTHON=$$PWD/venv/bin/python" >> .cronfile
	cat cron_jobs >> .cronfile
	crontab .cronfile
	rm .cronfile
	touch cron_jobs

setup: venv install_cron
	test -d logs || mkdir logs
	test -d archivo || mkdir archivo

clean:
	rm -rf venv/
	cat /dev/null | crontab
