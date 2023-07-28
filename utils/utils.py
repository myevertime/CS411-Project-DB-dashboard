from types import NoneType
from neo4j_utils import *
from mysql_utils import *
import pandas as pd
import plotly.graph_objs as go
import networkx as nx
import requests
import json
import openai
import os
import atexit

import concurrent.futures

# Keep API Key to credentials.py
from credentials import SERP_API_KEY
from credentials import OPENAI_API_KEY


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

# Function to fetch the latest publications for a given professor from Google Scholar
def fetch_google_scholar_publications(professor_name):
    # Use the SerpApi Google Scholar API
    # set up the request parameters
    params = {
        'api_key': f'{SERP_API_KEY}',
        'search_type': 'scholar',
        'q': f'{professor_name}',
        'sort_by' : 'date',
    }

    # make the http GET request to Scale SERP
    api_result = requests.get('https://api.scaleserp.com/search', params)

    data = api_result.json()

    # Access the "scholar_results" list and loop through its items
    publications = []
    if "scholar_results" in data.keys():
        for item in data["scholar_results"]:
            title = item["title"]
            link = item["link"]
            #snippet = item["snippet"]
            publication_info = f"**[{title}]({link})**\n" 
            publications.append(publication_info)
            return "\n".join(publications[:1])
    else:
        return "No search results from Google Scholars"

def generate_prompt(mongo_data, elements):
    prompt = ("Your role is to help students understand the professor."
    "Provide a short profile of the professor in a single sentence by using the information given below:\n"
    f"general info:'{mongo_data}'"
    f"network graph info:'{elements}'"
    "Please write in a **single sentence**")
    return prompt

def generate_summary_by_gpt(mongo_data, elements):
    openai.api_key = f"{OPENAI_API_KEY}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=[{"role": "system", "content": f"{generate_prompt(mongo_data, elements)}"}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        # Handle the exception here and provide a default response
        print(e)
        return "There was an error processing the request.\n\nPlease try again later."

def check_image_url(photoUrl):
    try:
        response = requests.get(photoUrl)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
import atexit
import mysql.connector

# Function to drop views on app termination
def drop_views_on_exit(view_lst):
    try:
        for view_name in view_lst:
            conn = mysql_connector()
            cursor = conn.cursor()
            drop_view_query = f"DROP VIEW IF EXISTS {view_name}"
            cursor.execute(drop_view_query)
            conn.commit()
            conn.close()
            print(f"View '{view_name}' dropped successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")