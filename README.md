# ODI

**ODI** is a project aiming at formally representing the narrative and structural elements of "Il castello dei destini incrociati" by Italo Calvino. In particular, **ODI** is the ontology describing the work, **BACODI** is the Knowledge Graph (KG) storing all data regarding the work. For a complete overview of the project please see the [documentation](https://odi-documentation.github.io/materials/).

The data can be browsed via this interface which provides several paths to explore BACODI KG along with some specific data-visualisations. 

This interface is a [Python 3](https://www.python.org/downloads/) web application built in [Flask](https://flask.palletsprojects.com/en/2.3.x/). 
The project is ongoing and under development.
 

## Web app Quick start

Clone this repository using the URL https://github.com/ValentinaPasqual/odi.git
or download the folder.

The project works with this **requirement**:

- [**Python**](https://www.python.org/downloads/) v3.6.3

Packages can be installed by running **setup.sh**:
```
sh setup.sh
```

After installing the required packages:

- Run **blazegraph.jar** locally:
```
cd data
java -server -Xmx4g -jar blazegraph.jar
```
- If the endpoint is empty, upload from the Blazegraph interface (**http://localhost:9999/**) both **data/odi.owl** and **data/bacodi.ttl**
- Update the path to the endpoint in **app.py** 

- Run **app.py**
- Open the application in your browser: **http://localhost:8000/**
