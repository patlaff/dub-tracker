from helpers.helpers import createLogger, conn

### CONFIG ###
logger = createLogger('db')

## SQL DB SETUP ###
def createTables():

    ### CONSTRUCTORS ###
    cur = conn.cursor()
    
    ## DUBS ##
    # with conn:
    #     conn.execute("DROP TABLE DUBS;")
    #     logger.info('Dropped Table, DUBS')
    
    with conn:
        cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='DUBS'")

    if cur.fetchone()[0]==1:
        logger.info('Table, DUBS, already exists.')
    else:
        logger.info('Table does not exist. Creating table, DUBS...')
        with conn:
            cur.execute("""
                CREATE TABLE DUBS (
                    message_id INTEGER NOT NULL PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    message_content INTEGER NOT NULL,
                    author TEXT NOT NULL,
                    date_sent TEXT NOT NULL,
                    dub_type TEXT
                );
            """)

    ## CONFIGS ##
    with conn:
        conn.execute("DROP TABLE CONFIGS;")
        logger.info('Dropped Table, CONFIGS')
    
    with conn:
        cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='CONFIGS'")

    if cur.fetchone()[0]==1:
        logger.info('Table, CONFIGS, already exists.')
    else:
        logger.info('Table does not exist. Creating table, CONFIGS...')
        with conn:
            cur.execute("""
                CREATE TABLE CONFIGS (
                    guild_id INTEGER NOT NULL PRIMARY KEY,
                    dt_channel_id INTEGER NOT NULL
                );
            """)
    
    cur.close()