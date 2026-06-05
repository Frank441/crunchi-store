from db.mongo import mongo as mongodb
from db.redis import redis_test as redisdb
from db.cassandra import evidencia_cassandra as cassandradb
from db.neo4j import evidencia_neo4j as neo4jdb


main():
    try:
        print("\n[*] Conectando a MongoDB...")
        mongo = mongodb.client()
        print("[*] Conectado a MongoDB")

        print("\n[*] Conectando a Redis...")
        redis = redisdb.ControladorRedisMarketplace()
        print("[*] Conectado a Redis")
        
        print("\n[*] Conectando a Cassandra...")
        cassandra = cassandradb.conectar_cassandra()
        print("[*] Conectado a Cassandra")

        print("\n[*] Conectando a Neo4j...")
        neo4j = neo4jdb.MotorRecomendacionNeo4j()
        print("[*] Conectado a Neo4j")

        router = Router(mongo, redis, cassandra, neo4j)
    

    except:
        Error("Error al conectar una de las bases de datos.")

if __name__ == "__main__":
    main()

class Router:
    _instance = None

    def __new__(cls, mongo, redis, cassandra, neo4j):
        if cls._instance is None:
            cls.instance = super(Router(), cls).__new__(cls)

            cls._instance.mongo = mongo
            cls._instance.redis = redis
            cls._instance.cassandra = cassandra
            cls._instance.neo4j = neo4j

        return cls._instance

    def getInstance():
        return _instance

