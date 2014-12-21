renaissance men
===============
### Non python dependencies
1. postgresql (>=9.3.5)
2. redis 
3. rabbitmq
4. libpq-dev
5. libpython-dev
6. nginx

#### setting up postgresql
1. create login role (username - 'renaissanceman', password - 'reddecemberwindows')
```sql
CREATE ROLE renaissanceman LOGIN
  ENCRYPTED PASSWORD 'md5c9108ae01386ce886d3cf97845d5a12b'
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
```
2. create db (name renaissance)
```sql
CREATE DATABASE renaissance
  WITH OWNER = renaissanceman
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'C'
       LC_CTYPE = 'UTF-8'
       CONNECTION LIMIT = -1;
```

#### setting up python environment
1. checkout git repository
2. create a new virtual environment 'renv'
```bash
virtualenv renv
```
3. install python dependencies
```bash
source renv/bin/activate
pip install -r renaissance_men/requirements.txt
```
4. migrate database schema
```bash
cd renaissance_men
alembic upgrade head
```
#### running server

```bash
source renv/bin/activate
python renaissance_men/server.py
```

#### redis data structures
key: services
value: set of service names

key: service_name:skills
value: set of service skills

key: service_name:providers
value: set of service provider id

key: sp:service_provider_id
value:
