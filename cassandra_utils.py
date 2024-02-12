import datetime
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from conf.config import settings
from loguru import logger

class CassandraUtils:
    def __init__(self):
        self.keyspace = settings.keyspace
        self.client_id = settings.client_id
        self.client_secret = settings.client_secret
        self.secure_connect_bundle_path = settings.secure_connect_bundle_path
        #logger.add(f"log/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log", level=settings.log_level)

    def generate_create_table_statements(self):
        create_table_statements = []
        
        logger.info(f"Fetching tables for keyspace: {self.keyspace}")
        
        session = self._connect_to_astra()
        
        tables = session.execute(f"SELECT * FROM system_schema.tables WHERE keyspace_name = '{self.keyspace}'")
        
        logger.info(f"Fetched tables")

        for table in tables:
            table_name = table.table_name
            create_stmt = f"CREATE TABLE {self.keyspace}.{table_name} ("
            
            columns = session.execute(f"SELECT * FROM system_schema.columns WHERE keyspace_name = '{self.keyspace}' AND table_name = '{table_name}'")
            pk = []
            ck = []
            for column in columns:
                create_stmt += f"\n  {column.column_name} {column.type},"
                if column.kind == 'partition_key':
                    pk.append(column.column_name)
                elif column.kind == 'clustering':
                    ck.append(column.column_name)
            
            if pk:
                create_stmt += f"\n  PRIMARY KEY ({'(' + ', '.join(pk) + ')' if len(pk) > 1 else pk[0]}"
                if ck:
                    create_stmt += f", {' '.join(ck)}"
                create_stmt += ")"
            
            create_stmt += "\n);"
            
            logger.info(create_stmt)
            
            create_table_statements.append(create_stmt)
        
        return create_table_statements

    def _connect_to_astra(self):
        auth_provider = PlainTextAuthProvider(self.client_id, self.client_secret)
        cloud_config= {
                'secure_connect_bundle': self.secure_connect_bundle_path
        }

        logger.info("Connecting to Astra database")
        
        cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
        session = cluster.connect()
        
        logger.info("Connected to Astra database")

        return session
