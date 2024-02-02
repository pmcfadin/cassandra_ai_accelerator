from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Function to fetch and generate CREATE TABLE statements
def generate_create_table_statements(session, config):
    keyspace = config['keyspace']

    create_table_statements = []
    
    tables = session.execute(f"SELECT * FROM system_schema.tables WHERE keyspace_name = '{keyspace}'")
    
    for table in tables:
        table_name = table.table_name
        create_stmt = f"CREATE TABLE {keyspace}.{table_name} ("
        
        columns = session.execute(f"SELECT * FROM system_schema.columns WHERE keyspace_name = '{keyspace}' AND table_name = '{table_name}'")
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
        create_table_statements.append(create_stmt)
    
    return create_table_statements

def connect_to_astra(config):
    client_id = config['client_id']
    client_secret = config['client_secret']
    secure_connect_bundle_path = config['secure_connect_bundle_path']
    keyspace = config['keyspace']
    logging = config["logging"]

    # Configure the connection
    auth_provider = PlainTextAuthProvider(client_id, client_secret)
    cloud_config= {
            'secure_connect_bundle': secure_connect_bundle_path
    }

    # Establish the connection
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    
    return session