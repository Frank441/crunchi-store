import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

_driver = None

def inicializar_neo4j():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return _driver

def cerrar_neo4j():
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None

def get_session():
    if _driver is None:
        raise RuntimeError("Neo4j no inicializado.")
    return _driver.session()