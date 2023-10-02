# ODI

**ODI** is a project which formally represents the narrative and structural elements of "Il castello dei destini incrociati" by Italo Calvino. In particular, **ODI** is the ontology describing the work, **BACODI** is the Knowledge Graph (KG) storing all data regarding the work. For a complete overview of the project please see the [documentation](https://odi-documentation.github.io/materials/).

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
- Upload both the ontology **data/odi.ttl** and the KG **data/bacodi.ttl** via the Blazegraph interface (accessible at **http://localhost:9999/**) [OR] Upload data via **cmd**

```
curl "http://localhost:9999/blazegraph/namespace/kb/sparql" --data-urlencode "update=DROP ALL; LOAD <[local-path]/data/bacodi.ttl>"  

curl "http://localhost:9999/blazegraph/namespace/kb/sparql" --data-urlencode "update=LOAD <[local-path]/data/odi.ttl>" 
```
A **blazegraph.jnl** file will be created in your **data** repository, no further data uploads are required. 

- Run **app.py**
```
python app.py
```
- Open the application in your browser: **http://localhost:8000/**

## Online Server Start
```
[15:08] Tommaso Vitale

service nginx start

/usr/bin/nohup /usr/lib/java/bin/java  -Dfile.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8 -server -Xmx2g  -Djetty.port=9999 -jar blazegraph.jar

nohup gunicorn -w 4 -b 0.0.0.0:8080 app:app
```
