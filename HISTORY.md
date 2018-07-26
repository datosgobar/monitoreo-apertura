0.0.10 (20-07-26)
-------------------

* Ahora es posible disparar la tarea de generación de reportes desde el admin de django, creando un `ReportGenerationTask`.

0.0.9 (20-07-23)
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