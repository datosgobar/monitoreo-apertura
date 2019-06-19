Versiones
=========
0.0.44 (11-06-19)
-------------------

* Actualiza versión de django_datajsonar
* Agrega endpoint de `/nodos-red-indicadores.csv`


0.0.43 (04-06-19)
-------------------

* Actualiza versiones de pydatajson y django_datajsonar


0.0.42 (29-05-19)
-------------------

* Overridea la función de import de indicadores para usar una asincrónica


0.0.41 (22-05-19)
-------------------

* Actualiza version de django_datajsonar para agregar la ruta nodes.csv y nodos.csv
* Agrega además el campo landingPage al admin de dataset 


0.0.40 (14-05-19)
-------------------

* Actualiza version de django_datajsonar para agregar la ruta nodes.json


0.0.39 (16-04-19)
-------------------

* Actualiza version de pydatajson


0.0.38 (16-04-19)
-------------------

* Actualiza y corrige logueo de sentry

0.0.37 (15-04-19)
-------------------

* Actualiza versión de django-datajsonar
* Agrega management command para importar/exportar csv de indicadores


0.0.36 (15-04-19)
-------------------

* Actualiza versión de pydatajson


0.0.35 (04-04-19)
-------------------

* Ordena las columnas de los csv de series de tiempo
* Revisión de nombres
* Fix del campo from en los mails
* Port a python 3
* Actualiza versión de pydatajson y django_datajsonar


0.0.34 (01-03-19)
-------------------

* Reordena apps del admin


0.0.33 (01-03-19)
-------------------

* Cambia el horario de mantenimiento a las 00:00
* Reutiliza las conexiones smtp para el envío de reportes
* Actualiza versión de pydatajson y django_datajsonar


0.0.32 (19-02-19)
-------------------

* Actualiza versión de pydatajson y django_datajsonar
* Revisón de nombres y refactor del admin
* Aseguro la existencia de un upkeep job para los synchronizers


0.0.31 (05-02-19)
-------------------

* Actualiza versión de django_datajsonar
* Fix a la recolección de indicadores de nodos federadores
* Restart de los workers en deploy


0.0.30 (17-01-19)
-------------------

* Actualiza versión de pydatajson


0.0.29 (16-01-19)
-------------------

* Singleton para modelo central
* Reportes de error cuando no se puede parsear un catálogo
* Actualiza versión de pydatajson y django_datajsonar


0.0.28 (21-12-18)
-------------------

* Nuevos modelo indicadores federadores.
* Series sobre los indicadores de los nodos federadores.
* Agrega logs del task de indicadores al reporte de staff.
* Actualiza versión de pydatajson.


0.0.27 (11-12-18)
-------------------

* Agrega management command para importar indicadores de un csv.


0.0.26 (4-12-18)
-------------------

* Agrega series de tiempo para indicadores de red y de nodos (`admin/indicadorred/series-indicadores` y `admin/indicador/<id de catalogo>/series-indicadores` respectivamente)


0.0.25 (28-11-18)
-------------------

* Agrega reportes de validación para los nodos de la red


0.0.24 (05-11-18)
-------------------

* Actualiza versión de pydatajson y django_datajsonar.
* Agrega documentación de synchronizers y config files.


0.0.23 (23-10-18)
-------------------

* Bugfix en reportes que llegaban vacíos.


0.0.22 (11-10-18)
-------------------

* Actualiza versión de pydatajson y django_datajsonar (Incluye los synchronizers).


0.0.22-prod (11-10-18)
-------------------

* Actualiza versión de pydatajson (No incluye los synchronizers).


0.0.21 (11-10-18)
-------------------

* En el command para borrar duplicados, me quedo con el último registrado.
* Separa las tareas en queues para hacer uso de los sincronizadores.
* Actualiza versión de django_datajsonar.


0.0.20 (8-10-18)
-------------------

* Fix en el deploy de rqscheduler. 


0.0.19 (5-10-18)
-------------------

* Actualiza versión de django_datajsonar. 
* Actualiza versión de pydatajson.
* Bugfix de generación de indicadores duplicados.


0.0.18 (19-09-18)
-------------------

* Actualiza versión de django_datajsonar.


0.0.17 (13-09-18)
-------------------

* Bugfix en el schedule form de reportes.
* Bugfix en la creación de corridas de federación. 


0.0.16 (5-09-18)
-------------------

* Actualiza versión de pydatajson.


0.0.15 (4-09-18)
-------------------

* Management command para programar tareas default.
* Form para simplificar la programación de tareas periódicas.


0.0.14 (29-08-18)
-------------------

* Actualiza versión de pydatajson.


0.0.12 (07-08-18)
-------------------

* Saca temporalmente acciones de top y bottom para los tipos de indicadores.


0.0.11 (03-08-18)
-------------------

* Agrega sección de resumen al reporte de indicadores.
* Permite ordenar los indicadores en el reporte.
* Permite ocultar indicadores del reporte.
* Ordena los indicadores no numéricos por valor de manera descendiente.


0.0.10 (26-07-18)
-------------------

* Ahora es posible disparar la tarea de generación de reportes desde el admin de django, creando un `ReportGenerationTask`.


0.0.9 (23-07-18)
-------------------

* Funcionalidad de mail de reporte de la red de nodos para los administradores de nodos.


0.0.8 (20-07-18)
-------------------

* Funcionalidad de mail de reporte de la red de nodos para usuarios staff.


0.0.7 (18-07-18)
-------------------

* Fix de timezones
* Migración para indicadores con ids faltantes.
* Usa nueva versión de django datajsonar con columna reviewed para datasets.


0.0.6 (12-07-18)
-------------------

* Agrega id de nodos a los indicadores.
* Genera los indicadores de red a partir de los nodos indexables.
* Actualiza la versión de `pydatajson` para calcular los 3 nuevos indicadores. 


0.0.5 (04-07-18)
-------------------

* Agrega help text de url de nodos (tag para probar el deploy).


0.0.4 (02-07-18)
-------------------

* Modelado de corridas de indicadores.
* Posibilidad de correr calculos de indicadores desde la UI.
* Descarga de datasets config files.
* Se dispara una corrida de federación al guardar un FederationTask desde la UI.
* Logueo de errores de federación y validación en FederationTask.


0.0.3 (19-06-18)
------------------

* Fijar versión de `pydatajson`.
* Arreglos en migraciones.


0.0.2 (13-06-18)
-------------------

* Arreglos para CD en staging. 


0.0.1 (13-06-18)
-------------------

* Incorporación de `django_datajsonar` con la posibilidad de modelar la red de nodos.
* Modelado de los nodos federadores y corridas de federación.
* Posibilidad de correr federaciones desde la UI.
