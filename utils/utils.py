from types import NoneType
from neo4j_utils import *
import pandas as pd
import plotly.graph_objs as go
import networkx as nx
import json

def query_neo4j_for_graph_data(faculty_name):
    driver = connect_to_neo4j()

    # Cypher query to get relevant nodes and their properties
    query = """
        MATCH (faculty:FACULTY {name: $facultyName})-[r1:AFFILIATION_WITH]->(institute:INSTITUTE)
        OPTIONAL MATCH (faculty)-[r2:INTERESTED_IN]->(keyword:KEYWORD)
        OPTIONAL MATCH (publication:PUBLICATION)-[r3:LABEL_BY]->(keyword)
        OPTIONAL MATCH (faculty)-[r4:PUBLISH]->(publication)
        RETURN faculty, institute, keyword, publication
        LIMIT 1
        """

    with driver.session(database="academicworld") as session:
        result = session.run(query, facultyName=faculty_name)
        return result.data()


def draw_networkgraph(faculty_name):
    network_data = query_neo4j_for_graph_data(faculty_name)
    
    # Create a DataFrame from the Neo4j query result
    df = pd.DataFrame(network_data)

    # Create a list to store the nodes and edges in Cytoscape format
    elements = []

    # Add faculty nodes to elements list
    for index, faculty_row in df.iterrows():
        faculty_data = faculty_row["faculty"]
        elements.append({
            "data": {
                "id": faculty_data["id"],
                "label": faculty_data["name"],
                **faculty_data  # Add all faculty properties to the node data
            },
            "classes": "faculty",
        })

    # Add institute nodes to elements list
    for index, institute_row in df.iterrows():
        institute_data = institute_row["institute"]
        elements.append({
            "data": {
                "id": institute_data["id"],
                "label": institute_data["name"],
                **institute_data  # Add all institute properties to the node data
            },
            "classes": "institute",
        })

    # Add keyword nodes to elements list
    for _, keyword_row in df.iterrows():
        keyword_data = keyword_row["keyword"]
        elements.append({
            "data": {
                "id": keyword_data["id"],
                "label": keyword_data["name"],
                **keyword_data  # Add all keyword properties to the node data
            },
            "classes": "keyword",
        })

    # Add publication nodes to elements list
    for _, publication_row in df.iterrows():
        publication_data = publication_row["publication"]
        elements.append({
            "data": {
                "id": publication_data["id"],
                "label": publication_data["title"],
                **publication_data  # Add all publication properties to the node data
            },
            "classes": "publication",
        })

    # Add edges for affiliation between faculty and institute
    for _, affiliation_row in df.iterrows():
        faculty_name = affiliation_row["faculty"]["id"]
        institute_name = affiliation_row["institute"]["id"]
        elements.append({"data": {"source": faculty_name, "target": institute_name, "label": "AFFILIATION_WITH"}})

    # Add edges for faculty interested in keywords
    for _, interest_row in df.iterrows():
        faculty_name = interest_row["faculty"]["id"]
        keyword_name = interest_row["keyword"]["id"]
        elements.append({"data": {"source": faculty_name, "target": keyword_name, "label": "INTERESTED_IN"}})

    for _, publish_row in df.iterrows():
        faculty_name = publish_row["faculty"]["id"]
        publication_title = publish_row["publication"]["id"]
        elements.append({"data": {"source": faculty_name, "target": publication_title, "label": "PUBLISH"}})

    for _, label_row in df.iterrows():
        publication_title = label_row["publication"]["id"]
        keyword_name = label_row["keyword"]["id"]
        elements.append({"data": {"source": publication_title, "target": keyword_name, "label": "LABEL_BY"}})

    return elements

def removeDanglingEdges(elements):
    vids = set([v['data']['id'] for v in elements if not 'source' in v['data']])
    return [e for e in elements if not 'source' in e['data'] or (e['data']['source'] in vids and e['data']['target'] in vids)]
