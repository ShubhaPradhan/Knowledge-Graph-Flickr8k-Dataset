import json

def build_imgid_to_filepath(json_path: str):
    """
    Reads a Flickr8k-style JSON file and returns a dictionary mapping:
    {
      0: "2513260012_03d33305cf.jpg",
      1: "2903617548_d3e38d7f88.jpg",
      ...
    }
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    images = data.get("images", [])
    
    imgid_to_filepath = {}
    for image_info in images:
        imgid = image_info.get("imgid")
        filename = image_info.get("filename")
        imgid_to_filepath[imgid] = filename

    return imgid_to_filepath

if __name__ == "__main__":
    json_file = "data/dataset_flickr8k.json"  # Replace with your actual JSON file path
    mapping = build_imgid_to_filepath(json_file)
    # make a json file
    with open("data/imgid_to_filepath.json", "w") as f:
        json.dump(mapping, f)
