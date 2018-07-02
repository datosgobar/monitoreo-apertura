# Uso

## Carga de Nodos

Despues de iniciar sesion como Administrador, debemos cargar un nuevo `Node Register file`.
Esta pagina se encuentra en la ruta `/admin/django_datajsonar/noderegisterfile/`.
Este archivo tiene un registro de los nodos _a federar_. Ese un archivo de extencion `.yml` y
tiene un aspecto como el siguiente:


```yaml
datosgobar:
  url: "http://datos.gob.ar/data.json"
  formato: "json"
  federado: false

transporte-bis:
  url: "http://datos.transporte.gob.ar/data.json"
  formato: "json"
  federado: false

# Mas nodos...
```

Luego de que creamos la nueva instancia, volvemos a la pagina del listado y deberiamos ver algo como 
la siguiente imagen:

![Node register file list](./images/node_register_file.png)

Luego seleccionamos la instancia y usamos la accion "Process node file", como se muestra en la imagen:

![Process Node register file list](./images/process_node_register_file.png)

Eso procesara el archivo (puede tardar un poco), y al terminar veremos los nodos detectados en
`/admin/django_datajsonar/node/`, algo parecido a

![Nodes list](./images/nodes_list.png)


## Lectura de catalogos

Para lanzar una lectura de todos los catalogos de los nodos, podemos instancia una `ReadDataJsonTask`.
Para eso nos dirigimos a la ruta `/admin/django_datajsonar/readdatajsontask/`.
Esta instancia no requiere ningun parametro, ya que leera los datos necesarios de las instancias `Node`
del proceso anterior.
Esta instancia ira registrando los "logs" y "resultados" del proceso. Podremos ver algo como:

![Read DataJson Task](./images/read_datajson_task.png)

### Cierre de la tarea

Por una cuestion de concurrencia, las tareas no quedaran en estado "Finalizada" por si solas.
Para que el sistema verifique es estado de las tareas, debemos instanciar un `RepeatableJob`.
Para eso vamos a la ruta `/admin/scheduler/repeatablejob/`.

En el campo **nombre** podemos poner lo que deseemos (como ""), en el campo **callable** debemos
poner `django_datajsonar.indexing.tasks.close_read_datajson_task`.
En el campo **Queue** ponemos `indexing`.
En los campos **fecha** y **hora** de **scheduled time** hacemos click en "Hoy" y "Ahora".
Finalmente en **interval** ponemos `10` y en **interval unit** `minutes`.
Luego de guardar la instancia deberiamos tener algo como:

![Close Read DataJson Task](./images/close_read_datajson_task.png)


### Lectura periodica 

Para que la lectura de los catalogos se ejecute periodicamente, debemos crear un `RepeatableJob`.

Para eso vamos a la ruta `/admin/scheduler/repeatablejob/`.

En el campo **nombre** podemos poner lo que deseemos (como "New Read Datajson Task"), en el campo **callable** debemos
poner `django_datajsonar.tasks.schedule_new_read_datajson_task`.
En el campo **Queue** ponemos `indexing`.
Habilitar el campo **Enabled**.
En los campos **fecha** y **hora** de **scheduled time** hacemos click en "Hoy" y "Ahora".
Finalmente en **interval** ponemos `1` y en **interval unit** `days`.
Luego de guardar la instancia deberiamos tener algo como:

![New Read DataJson Task](./images/new_read_datajson_task.png)

## Generación de indicadores

Hay 2 formas de comenzar una corrida de generación de indicadores de la red de nodos: podemos instanciar una
Corrida de indicadores. Para eso nos dirigimos a la ruta `/admin/dashboard/indicatorsgenerationtask/`.
Esta instancia no requiere ningun parametro, lee los catálogos a partir de la librería de Github.
Estas instancias registran los "logs" y "resultados" del proceso. Podremos ver algo como:

![Indicators Generation Task](./images/indicators_generation_task.png)

La otra forma es mediante un management command de Django. El comando `python manage.py indicadores` dispara de manera
sincrónica una tarea de generación de indicadores. De la misma manera que el anterior, el resultado se guarda en los
logs del `IndicatorsGenerationTask` correspondiente.

### Generación periódica 

Para que la lectura de los catalogos se ejecute periodicamente, debemos crear un `RepeatableJob`.

Para eso vamos a la ruta `/admin/scheduler/repeatablejob/`.

En el campo **nombre** podemos poner lo que deseemos (como "Generación indicadores"), en el campo **callable** debemos
poner `monitoreo.apps.dashboard.indicators_tasks.indicators_run`.
En el campo **Queue** ponemos `indexing`.
Habilitar el campo **Enabled**.
En los campos **fecha** y **hora** de **scheduled time** hacemos click en "Hoy" y "Ahora".
Finalmente en **interval** ponemos `1` y en **interval unit** `days`.
Luego de guardar la instancia deberiamos tener algo como:

![Generación indicadores](./images/generacion_indicadores.png)
