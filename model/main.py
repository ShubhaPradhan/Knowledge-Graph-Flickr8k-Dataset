import os
import ssl
import json
import logging
from openie import StanfordOpenIE
from py2neo import Graph, Node, Relationship

########################################################################
# 0. SSL Context & Environment Setup
########################################################################

# Disable SSL certificate checks (not recommended for production).
ssl._create_default_https_context = ssl._create_unverified_context

# Set CORENLP_HOME to your local CoreNLP folder if needed:
os.environ["CORENLP_HOME"] = "/Users/shubhapradhan/Documents/stanford-corenlp-4.5.7"

########################################################################
# 1. Synonym Dictionary (Optional)
########################################################################

synonyms_dict = {
    "kids": "child",
    "kid": "child",
    "baby": "child",
    "babies": "child",
    "children": "child",
    "truck": "car",
    "trucks": "car",
    "cars": "car",
    # Extend as needed...
}

def canonicalize_text(text: str) -> str:
    """
    Simple approach: for each word, if it appears in synonyms_dict, replace it.
    """
    words = text.split()
    new_words = []
    for w in words:
        lw = w.lower()
        new_words.append(synonyms_dict.get(lw, w))
    return " ".join(new_words)

########################################################################
# 2. Neo4j Integration
########################################################################

# Connect to Neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

def merge_entity(name: str) -> Node:
    """
    Merge or create an Entity node with the given name.
    """
    node = Node("Entity", name=name)
    graph.merge(node, "Entity", "name")
    return node

def set_entity_attribute(entity_node: Node, attr_name: str, attr_value: str):
    """
    Dynamically set an attribute on the entity node (e.g., color='black').
    """
    entity_node[attr_name] = attr_value
    graph.push(entity_node)

def create_relationship(subj_node: Node, relation: str, obj_node: Node, imgid):
    """
    Create a relationship from subj_node to obj_node with the given verb/rel label.
    Attach an 'imgid' property so we know which image it's from.
    """
    rel = Relationship(subj_node, relation.upper(), obj_node)
    rel["imgid"] = imgid
    graph.merge(rel)

########################################################################
# 3. Stanford OpenIE-based Extraction
########################################################################

# Initialize a *single* StanfordOpenIE client for the entire script.
client = StanfordOpenIE()

def extract_triples_openie(sentence: str):
    """
    Extract triples using the global StanfordOpenIE client.
    """
    return client.annotate(sentence)

def handle_triple(subject: str, relation: str, obj: str, imgid):
    """
    Process one triple. If the relation looks like an attribute, store it;
    otherwise treat it as a relationship.
    """
    subject_canon = canonicalize_text(subject)
    object_canon = canonicalize_text(obj)

    subj_node = merge_entity(subject_canon)
    rel_lower = relation.lower()

    # Example logic: if the relation contains certain keywords, treat them as attributes
    known_attribute_keywords = [
        "color", "colour", "size", "height", "width", "age", "material", 
        "shape", "position", "movement", "action", "emotion", "expression", 
        "interaction", "activity", "type", "direction", "surface", "distance", 
        "category", "weather", "clothing", "object", "animal"
    ]
    for kw in known_attribute_keywords:
        if kw in rel_lower:
            # Set the object text as an attribute on the subject node
            set_entity_attribute(subj_node, kw, object_canon)
            return

    # If none of those keywords matched, treat it as a relationship
    obj_node = merge_entity(object_canon)
    create_relationship(subj_node, relation, obj_node, imgid)

########################################################################
# 4. Progress Checkpointing
########################################################################

PROGRESS_FILE = "progress.json"

def load_progress():
    """
    Load a JSON file storing the last processed imgid. 
    Returns a dict like {"last_processed": -1} if not found.
    """
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"last_processed": -1}

def save_progress(imgid):
    """
    Save the last processed imgid to a JSON file.
    """
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"last_processed": imgid}, f)

########################################################################
# 5. Main Processing Logic
########################################################################

logging.basicConfig(
    filename="output.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Script started.")

def process_caption(caption: str, imgid):
    """
    Extract all triples from a single caption, store them in Neo4j.
    """
    triples = extract_triples_openie(caption)
    logging.info(f"OpenIE extracted from '{caption}': {triples}")

    for triple in triples:
        subject = triple.get("subject")
        relation = triple.get("relation")
        obj = triple.get("object")

        if subject and relation and obj:
            handle_triple(subject, relation, obj, imgid)


def main():
    """
    Main function to load dataset, skip already processed images, 
    and store new relationships in Neo4j.
    """
    try:
        with open("./data/dataset_flickr8k.json", "r") as f:
            data = json.load(f)
            logging.info("JSON file loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load JSON file: {e}")
        return

    images = data.get("images", [])
    progress_info = load_progress()
    last_done = progress_info["last_processed"]

    logging.info(f"Resuming from last processed imgid={last_done}")

    for image_info in images:
        imgid = image_info.get("imgid", -1)
        if imgid <= last_done:
            continue  # already processed

        # Process all captions for this image
        sentences = image_info.get("sentences", [])
        for sentence_info in sentences:
            caption_text = sentence_info.get("raw", "")
            process_caption(caption_text, imgid)

        # Update progress after this image is fully processed
        save_progress(imgid)
        logging.info(f"Image {imgid} processed. Progress saved.")

    logging.info("All images processed successfully.")
    logging.info("Script completed successfully.")

if __name__ == "__main__":
    main()
