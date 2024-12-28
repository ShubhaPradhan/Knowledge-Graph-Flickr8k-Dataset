import json
import gradio as gr
from py2neo import Graph

# Connect to Neo4j (update credentials or URI if needed)
graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

# Load {imgid: filename} mapping
with open("./data/imgid_to_filepath.json", "r") as f:
    id_to_fname = json.load(f)

def search_images(entity_name: str):
    """
    Given an entity name (e.g., 'child'), find all image IDs in Neo4j
    that reference that entity, then return the corresponding image files.
    """
    query = """
    MATCH (s:Entity)-[r]-(o:Entity)
    WHERE s.name = $entity_name OR o.name = $entity_name
    RETURN DISTINCT r.imgid AS imgid
    """
    result = graph.run(query, entity_name=entity_name)
    
    img_ids = [record["imgid"] for record in result]
    
    image_paths = []
    for img_id in img_ids:
        str_id = str(img_id)
        if str_id in id_to_fname:
            # Adjust the path as needed if your images are in a subfolder
            image_paths.append("Flickr8k_Dataset/" + id_to_fname[str_id])
    
    return image_paths

def run_cypher_query(cypher_query: str):
    """
    Run an arbitrary Cypher query.
    Then parse out the imgid from the result,
    look up the filenames, and return them.
    WARNING: This is dangerous if you allow untrusted users to run 
    arbitrary queries on your database!
    """
    result = graph.run(cypher_query)
    records = list(result)

    # Print all records for debugging
    print(records, "Raw Cypher Query Results")

    # Extract `imgid` from each record
    img_ids = [rec["imgid"] for rec in records]
    print(img_ids, "Extracted img_ids")

    # Find corresponding file paths
    image_paths = []
    for img_id in img_ids:
        str_id = str(img_id)
        print(str_id, "Converted img_id to string")
        if str_id in id_to_fname:
            print(id_to_fname[str_id], "Found filename for img_id")
            image_paths.append("Flickr8k_Dataset/" + id_to_fname[str_id])

    return image_paths


# Build a tabbed Gradio interface with two tabs:
# 1) "Entity Name Query"
# 2) "Custom Cypher Query"
with gr.Blocks() as demo:
    gr.Markdown("## Neo4j + Gradio Demo")

    with gr.Tabs():
        # First tab: Search by entity name
        with gr.TabItem("Entity Name Query"):
            entity_input = gr.Textbox(label="Enter an entity name (e.g., 'child')")
            search_button = gr.Button("Search")
            entity_gallery = gr.Gallery(label="Matching Images from Neo4j")
            
            # Link the button click to the search_images function
            search_button.click(fn=search_images, inputs=entity_input, outputs=entity_gallery)

        # Second tab: Arbitrary Cypher query
        with gr.TabItem("Custom Cypher Query"):
            cypher_input = gr.Textbox(label="Enter any Cypher query")
            query_button = gr.Button("Run Query")
            cypher_gallery = gr.Gallery(label="Results")

            # Link the button click to the run_cypher_query function
            query_button.click(fn=run_cypher_query, inputs=cypher_input, outputs=cypher_gallery)

# Launch the app
if __name__ == "__main__":
    demo.launch()
