# Neo4j-Powered Image Search Tool

## Overview
This project is a **Neo4j-powered image search application** that uses natural language processing (NLP) to extract entities and relationships from image captions and store them in a graph database. Users can search for images based on these entities or run custom Cypher queries through a user-friendly Gradio interface.

## Key Features
- **Entity-Based Search**: Retrieve images by searching for specific entities (e.g., "child" or "car").
- **Custom Cypher Queries**: Advanced users can write and execute Cypher queries to explore relationships and retrieve relevant images.
- **Stanford OpenIE Integration**: Extracts triples (subject, relation, object) from image captions for semantic representation in the Neo4j database.
- **Synonym Normalization**: Ensures related terms (e.g., "kids" and "children") are treated as the same entity for better search accuracy.
- **Gradio Interface**: Provides a tabbed interface for both simple searches and advanced query options.

## How It Works
1. **Caption Processing**:
   - Captions from the Flickr8k dataset are processed using Stanford OpenIE to extract semantic triples.
   - These triples are stored in a Neo4j graph database, with entities as nodes and relationships as edges.
2. **Image Mapping**:
   - Each image is associated with a unique `imgid`, mapped to its file path.
3. **Search Functionality**:
   - Users can search for images by entering an entity name, or execute Cypher queries to explore the graph directly.

## Setup Instructions

### Prerequisites
- Python 3.8+
- Neo4j installed and running locally
- Stanford CoreNLP downloaded and set up
- Gradio library installed
- Flickr8k dataset (or another dataset with captions and images)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/neo4j-image-search.git
   cd neo4j-image-search
   ```
2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up Neo4j:
   - Start the Neo4j server.
   - Update the `graph` connection in the code with your Neo4j credentials.
4. Download Stanford CoreNLP:
   - Place it in a directory (e.g., `/path/to/stanford-corenlp`).
   - Set the `CORENLP_HOME` environment variable to this path.
5. Prepare the dataset:
   - Place the Flickr8k dataset in a folder (e.g., `Flickr8k_Dataset`).
   - Modify the JSON mapping paths in the code to match your setup.

### Running the Application
1. Start the Neo4j server.
2. Launch the Gradio app:
   ```bash
   python app.py
   ```
3. Open the app in your browser at `http://127.0.0.1:7860/`.

## Usage
- **Entity Name Query**: Enter an entity name (e.g., "child") in the first tab to find related images.
- **Custom Cypher Query**: Use the second tab to enter any valid Cypher query for advanced searches.

## Folder Structure
```
neo4j-image-search/
├── data/
│   ├── dataset_flickr8k.json  # Flickr8k dataset JSON file
│   ├── imgid_to_filepath.json # Mapping of imgid to file paths
├── app.py                     # Gradio app script
├── triple_extraction.py       # Stanford OpenIE integration and processing
├── graph_integration.py       # Neo4j database integration
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## Future Enhancements
- Add support for more datasets.
- Enhance NLP processing with additional extraction techniques.
- Integrate more advanced search capabilities (e.g., fuzzy matching, similarity search).

## License
This project is licensed under the MIT License.

## Contact
For questions or feedback, feel free to reach out to [your email/contact info].
