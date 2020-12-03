# PsycoSSH

A ConnectionFactory for use by psycopg2 to enable SSH Tunneling

Probably should just use `create_tunneled_engine` which wraps around it

### Example

```python
from psycossh import create_tunneled_engine
from sqlalchemy import MetaData

engine = create_tunneled_engine(
    ssh_user="ssh_username",
    ssh_pkey=r"C:\Path\To\OpenSSH_Private_Key",  # without password
    ssh_host=r"ssh_server_host",
    ssh_port=22,  # default value  

    database=r"main_db",
    pg_host="localhost",  # default value
    pg_port=5432,  # default value
    pg_password="pg_password"
)
meta = MetaData()
meta.reflect(bind=engine)
print(meta.tables)
```
