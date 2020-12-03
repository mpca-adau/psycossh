# coding=utf-8
from timeit import default_timer as timer

from psycopg2.extensions import connection, make_dsn, parse_dsn
from sqlalchemy import create_engine
from sshtunnel import open_tunnel


class TunneledConnection(connection):
    """A ConnectionFactory for use by psycopg2 to enable SSH Tunneling

    Can either accept ssh properties via the connection url (dsn) or via class variables

    Examples:
        Connect to a host where the postgres user is the same as the SSH user, they are on the same host, and default
        ports are used.  No password is set for the Postgres user

             .. code-block:: python

                engine = create_engine(
                    'postgresql://{user}:{password}@{host}/{db}'.format(
                            user=ssh_user,
                            password=ssh_pkey,
                            host=ssh_server,
                            db=postgres_db),
                    connect_args={'connection_factory': TunneledConnection}

        Alternatively, various options can be set in advance on the class.
    """

    ssh_user = None
    ssh_pkey = None
    ssh_host = None
    ssh_port = None
    pg_host = None
    pg_user = None
    pg_port = None
    pg_password = None
    _tunnel_connections = {}

    def __init__(self, dsn, *args, **kwargs):
        cparams = parse_dsn(dsn)
        ssh_user = self.__class__.ssh_user or cparams["user"]
        ssh_pkey = self.__class__.ssh_pkey or cparams["password"]
        ssh_host = self.__class__.ssh_host or cparams["host"]
        ssh_port = self.__class__.ssh_port or 22
        pg_port = self.__class__.pg_port or cparams.get("port", None) or 5432
        pg_user = self.__class__.pg_user or cparams["user"]
        pg_server = self.__class__.pg_host or "localhost"
        pg_password = self.__class__.pg_password or None
        tun_spec = (ssh_host, ssh_port, ssh_user, ssh_pkey, pg_server, pg_port)
        if tun_spec not in self.__class__._tunnel_connections:
            print("Creating Tunnel {}".format(tun_spec))
            self.__class__._tunnel_connections[tun_spec] = open_tunnel(
                ssh_address_or_host=(ssh_host, ssh_port),
                ssh_username=ssh_user,
                ssh_pkey=ssh_pkey,
                remote_bind_address=(pg_server, pg_port),
                local_bind_address=("127.0.0.1",),
                compression=True,
                block_on_close=False,
            )
            self.__class__._tunnel_connections[tun_spec].start()
        cparams["host"] = "localhost"
        cparams["port"] = self.__class__._tunnel_connections[tun_spec].local_bind_port
        cparams["password"] = pg_password
        cparams["user"] = pg_user
        start = timer()
        super(TunneledConnection, self).__init__(make_dsn(None, **cparams), *args)
        print("{:0.2f}".format(timer() - start))


def create_tunneled_engine(
    ssh_host,
    ssh_user,
    ssh_pkey,
    database,
    ssh_port=22,
    pg_host="localhost",
    pg_user=None,
    pg_port=5432,
    pg_password=None,
    **kwargs,
):

    if pg_user is None:
        pg_user = ssh_user

    class _OurTunneledConnection(TunneledConnection):
        pass

    _OurTunneledConnection.ssh_host = ssh_host
    _OurTunneledConnection.ssh_user = ssh_user
    _OurTunneledConnection.ssh_pkey = ssh_pkey
    _OurTunneledConnection.ssh_port = ssh_port
    _OurTunneledConnection.pg_host = pg_host
    _OurTunneledConnection.pg_user = pg_user
    _OurTunneledConnection.pg_port = pg_port
    _OurTunneledConnection.database = database
    _OurTunneledConnection.pg_password = pg_password
    return create_engine(
        "postgresql://{user}@{host}/{database}".format(
            user=pg_user, host=ssh_host, database=database
        ),
        connect_args={"connection_factory": _OurTunneledConnection},
        **kwargs
    )


__all__ = ["create_tunneled_engine"]
