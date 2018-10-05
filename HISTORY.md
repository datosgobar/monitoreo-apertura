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

* Actualiza versión de pydatajson


0.0.12 (07-08-18)
-------------------

* Saca temporalmente acciones de top y bottom para los tipos de indicadores


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

* Funcionalidad de mail de reporte de la red de nodos para los administradores de nodos

0.0.8 (20-07-18)
-------------------

* Funcionalidad de mail de reporte de la red de nodos para usuarios staff

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

* Incorporación de `django_datajsonar` con la posibilidad de modelar la red de nodos
* Modelado de los nodos federadores y corridas de federación.
* Posibilidad de correr federaciones desde la UI