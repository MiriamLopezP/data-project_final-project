
# EDA Austin Animal Center

## Descripción del proyecto

Este proyecto desarrolla un análisis exploratorio de datos (EDA) sobre los registros de entradas y salidas de animales de un centro de protección animal de Austin. El objetivo principal es entender la composición del conjunto de datos, mejorar su calidad, unir correctamente los episodios de entrada y salida de cada animal y extraer patrones útiles sobre permanencia, tipos de animales, tipos de salida y posibles anomalías de registro.

El trabajo se ha realizado en dos partes complementarias. En primer lugar, se ha desarrollado un codigo en Python para la carga, revisión de calidad, limpieza, transformación, generación de variables derivadas, fusión de datasets y análisis descriptivo y estadístico. En segundo lugar, se ha utilizado Excel como herramienta de apoyo para la visualización, exploración interactiva y construcción de dashboards.

Más concretamente, el proyecto parte de dos conjuntos de datos independientes:

* `Austin_Animal_Center_Intakes.csv`: registros de entrada de animales al centro
* `Austin_Animal_Center_Outcomes.csv`: registros de salida de animales del centro.

A partir de ambos ficheros se construye un dataset final unificado, `animal_center_final.csv`, que permite analizar cada episodio de estancia de forma holistica.

---

## Objetivos del análisis

Los objetivos principales del proyecto han sido los siguientes:

* Revisar la calidad inicial de los datasets originales.
* Limpiar y homogeneizar variables
* Crear una clave de episodio que permita distinguir varias entradas y salidas del mismo animal.
* Transformar la edad en texto a una medida numérica comparable en días.
* Crear nuevas variables útiles para el análisis, como grupo de edad, sexo, estado reproductivo, tipo deraza, indicador de outcome y duración de estancia
* Unir los datasets de intakes y outcomes en una única tabla final .
* Detectar registros problemáticos o anómalos, como estancias negativas o registros sin salida asociada.
* Obtener estadísticas descriptivas y relaciones básicas entre variables.
* Complementar el análisis con visualizaciones y dashboards con Excel.

---

## Estructura del proyecto


├── data/
│   ├── raw/
│   │   ├── Austin_Animal_Center_Intakes.csv
│   │   └── Austin_Animal_Center_Outcomes.csv
│   └── processed/
│       ├── intakes_clean.csv
│       ├── outcomes_clean.csv
│       └── animal_center_final.csv
├── src/
│   └── codigo.py
├── tables/
│   ├── review_intakes_data.csv
│   ├── review_outcomes_data.csv
│   ├── merge_quality.csv
│   ├── numeric_summary.csv
│   ├── animals_by_type.csv
│   ├── animals_by_age_group.csv
│   ├── outcomes_by_type.csv
│   ├── stay_by_outcome_type.csv
│   ├── stay_by_animal_type.csv
│   ├── monthly_intakes.csv
│   (...)
│   
│   
├── excel/
│   └── Animal_Center_Final_Dashboard.xlsx
└── README.md
```

---

## Requisitos

Este proyecto se ha elaborado con Python y utiliza las librerías:

* pandas
* numpy
phyton3 install pandas numpy

Para ejecutar el análisis necesitamos la siguiente estructura de carpetas:

* `data/raw/` con los dos CSV originales
* `data/processed/` para guardar los datos limpios y mergeados
* `tables/` para exportar las tablas resumen


### 1. Carga de datos

El análisis comienza cargando los dos datasets crudos: uno de entradas y otro de salidas. A partir de ellos se construye todo el flujo posterior.

### 2. Revisión inicial de calidad

Antes de transformar los datos se comprueban:

* número de filas y columnas
* filas completamente duplicadas
* existencia de identificadores nulos
* número de animales únicos
* número de registros en los que un mismo animal aparece repetido
* coincidencia entre `DateTime` y `MonthYear`


### 3. Limpieza y normalización de tpos

Las variables de tipo texto se normalizan para evitar inconsistencias por espacios, vacíos o formatos diferentes. Para ello:

* se convierten a tipo string, se eliminan espacios sobrantes y los textos vacíos se sustituyen por valores nulos.

Este paso es importante porque mejora la consistencia de variables categóricas: raza, sexo, tipo de entrada o condición del animal.

### 4. Eliminación de registros problemáticos básicos

En ambos datasets se eliminan:

* registros sin `Animal ID` y filas duplicadas exactas.

Esto evita que el análisis posterior se vea afectado por observaciones irrelevantes o repetidas.

### 5. Conversión de fechas y orden temporal

Las variables temporales de entradas y salidas se convierten a formato datetime. Esto permite ordenar cronológicamente los eventos de cada animal y trabajar posteriormente con años, meses, días, duración de estancia..

### 6. Construcción del episodio (`case_id`)

Un mismo animal puede entrar más de una vez al centro, por lo que `Animal ID` no es suficiente como clave analítica.

Para resolverlo:

* se ordenan los registros de cada animal por fecha,
* se genera un `event_number` con un contador acumulado para cada animal
* se crea una clave de episodio llamada `case_id` compuesta por `animal_id + event_number`

Esto permite tratar correctamente cada estancia como una unidad independiente de análisis.

### 7. Transformación de la edad a días

Para poder analizarla numéricamente, se transforma a una variable continua en días
### 8. Creación de grupos de edad

Se construye una clasificación por grupos:

* 0-1 month
* 1-6 months
* 6-12 months
* 1-3 years
* 3-7 years
* 7+ years
* Unknown

Esto hace más interpretable el análisis descriptivo

### 9. Descomposición del sexo y estado reproductivo

La variable original de sexo contenía información combinada, por ejemplo sobre el sexo biológico y si el animal estaba esterilizado o no. Por ello se divide en dos columnas. Así se gana claridad analítica y se facilita el recuento por categorías.

### 10. Separación de colores

La variable de color se divide en dos columnas cuando aparecen dos colores separados por `/`. Con esto se descompone una categoría compleja en dos elementos más útiles.

### 11. Clasificación del tipo de raza

Se crea la variable `breed_type` para diferenciar entre:

* `Mixed`, cuando la raza contiene `Mix` o `/`
* `Pure`, en caso contrario

Esta transformación permite estudiar si predominan animales mestizos o de raza pura.

### 13. Fusión de datasets

Una vez limpios ambos conjuntos, se realiza un merge por `animal_id` y `event_number`, en lugar de usar solo el identificador del animal, clave, porque garantiza un emparejamiento más preciso entre cada entrada y su posible salida asociada. La fusión se hace con un `left join` desde intakes, de manera que:

todos los registros de entrada se conservan; si existe una salida compatible, se añade y si no existe, se queda como episodio sin outcome asociado.

### 14. Creación de columnas extras:

Tras la unión se generan:

* `has_outcome_record`: indica si el caso tiene salida registrada.
* `negative_stay_anomaly`: detecta si la fecha de salida es anterior a la fecha de entrada.

Estas variables permiten evaluar como de bueno es un matching y detectar posibles errores de registro y anomalias.

### 15. Cálculo de la longitud de estancia

La longitud de estancia se calcula como la diferencia entre `outcome_datetime` e `intake_datetime` en días.

Cuando la estancia resultante es negativael registro se marca como anomalía y la longitud de estancia se sustituye por nulo para no contaminar nuestros datos

Esta decisión es metodológicamente correcta porque evita incorporar valores imposibles al análisis cuantitativo.


Los resutlados se exportan obteniendo como se ha dicho anteriormente: los datasets limpios de intakes y outcomes, el dataset final fusionado y múltiples tablas con summaries descriptivos/estadísticos.

dejando preparados los datos para análisis adicional de Excel.

---

## Resultados del análisis descriptivo

### Dimensión de los datos

* Dataset original de intakes: 124120 filas y 12 columnas
* Dataset original de outcomes: 124491 filas y 12 columnas
* Dataset final fusionado: 124101 filas y 34 columnas

Reducción respecto al dataset original por eliminación de duplicados exactos durante la limpieza

* No había `Animal ID` nulos en ninguno de los dos datasets
*  existían duplicados exactos
* muchos animales aparecen repetidos porque habían tenido más de un episodio de entrada al centro
* `DateTime` y `MonthYear` coincidían fila a fila.

### Merge

Tras la fusión: 23543 registros presentan outcome asociado,558 registros no presentan outcome, 694 registros muestran estancia negativa y por tanto se consideran anomalías.

emparejamiento muy alto pero no perfecto, y que existe una pequeña fracción de episodios incompletos/inconsistentes.

### Outcome del analisis:

La mayoría de los registros corresponden claramente a perros y gatos (70438 y 46448 respectivamente)

En el momento de entrada predominan ligeramente los machos sobre las hembras, aunque ambas categorías son muy próximas. También destaca que la mayoría de los animales aparecen como intactos, o sea no esterilizados (lo cual tiene sentido).

Los grupos de edad más frecuentes son:

* 1-3 years: 40816
* 1-6 months:28508
* 3-7 years: 18674
* 0-1 month: 15691

redominan claramente los animales mestizos:

* Mixed: 102345
* Pure: 21756

Adopción, transferencia y devolución al propietario concentran la mayor parte de las salidas registradas.

* Adoption: 54742
* Transfer: 36489
* Return to Owner: 21456
* Euthanasia: 8337


La duracion de laestancia presenta una distribución muy asimétrica hacia la derecha. La diferencia entre media vs mediana refleja una fuerte presencia de valores extremos de larga permanencia.


* media: 18.46 días
* mediana: 5.12 días
* desviación típica: 43.06 días
* mínimo: 0.00 días
* máximo:1521.98 días

La estancia varía claramente según el tipo de salida. Los animales adoptados permanecen más tiempo en el centro que los devueltos a propietarios.

* adoption: media 32.52 días
* Transfer: media 9.38 días
* Return to Owner: media 3.50 días
* Euthanasia: media 5.27 días

Los volúmenes más altos de entradda y salida de animales se concentran especialmente en meses de primavera y verano.

---

## Resultados del análisis estadístico

### Cuantiles 

longitud de estancia: el 50% central de las estancias se sitúa aproximadamente entre 1.38 y 15.23 días

* percentil 25: 1.38 días
* mediana: 5.12 días
* percentil 75: 15.23 días

La desviación típica y la varianza muestran que la permanencia es una variable muy dispersa, especialmente en categorías como adopción o livestock. Esto significa que, aunque existan patrones generales, hay también una gran diversidad en los diferentes casos.

La  edad no parece ser una variable predictiva fuerte de la duración de la estancia




## Análisis en Excel


### Hoja de visualización de outliers y anomalías
En esta hoja se desarrollaron varios análisis específicos:

#Distribución de la estancia y detección de valores atípicos: Se estudió la variable `length_of_stay_days` mediante

* gráfico de caja y bigotes
* media
* mediana
* mínimo
* máximo
* desviación típica.

La media resultó bastante superior a la mediana, lo que confirma que la distribución está sesgada a la derecha. Además, se aplicó el criterio del rango intercuartílico (IQR) para detectar valores atípicos, considerando como casos excepcionales aquellos por encima del límite superior.

#Registros con outcome y sin outcome: Se analizó la variable `has_outcome_record` para evaluar la completitud del emparejamiento entre intakes y outcomes. Los registros sin outcome se interpretan como posibles casos abiertos o episodios sin salida vinculada en el dataset disponible.

#Estancias negativas: Se analizó  la variable `negative_stay_anomaly`, que identifica casos en los que la salida fue registrada antes que la entrada. Estos episodios se interpretan como anomalías o errores de registro

####Relación entre edad de entrada y estancia: un gráfico de dispersión para estudiar la posible relación entre `intake_age_days` y `length_of_stay_days`. El gráfico no sugiere una relación lineal fuerte. La mayoría de los animales entra siendo joven y permanece poco tiempo, aunque existen algunos casos extremos con estancias largas que no siguen un patrón claro.

### Hoja de estudio de datos, tablas dinámicas y gráficos

En esta hoja se construyeron tablas dinámicas y gráficos asociados para explorar el dataset desde distintos ángulos. Entre los análisis incluidos se encuentran: recuento total de animales por tipo, evolución temporal de intakes y outcomes, clasificación por edades de entrada, comparación entre intake type y outcome type,..


### Dashboard interactivo con segmentadores para filtrar la información, resumir rápidamente los datos más importantes yapoyar la extracción de conclusiones de forma mas visual.


---

Como posibles ampliaciones del proyecto se podría profundizar en los factores que explican estancias largas, estudiar diferencias por intake type y outcome subtype con mayor detalle,...

---

## Contribuciones

Las contribuciones son bienvenidas.



## Autor

-Miriam Lopez Puerto
-https://github.com/MiriamLopezP



