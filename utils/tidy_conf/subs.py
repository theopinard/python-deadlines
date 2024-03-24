from tqdm import tqdm
import yaml


def auto_add_sub(data):
    """Automatically add a subfield to the data based on the conference name.

    This function uses a list of keywords to match the conference name to a subfield.
    """
    keywords = load_subs()
    for i, q in tqdm(enumerate(data.copy()), total=len(data)):
        if "sub" not in q:
            for key, value in keywords.items():
                if any(word in q["conference"].lower() for word in value):
                    print(f"Adding sub {key} to {q['conference']}")
                    data[i]["sub"] = key
                    break
    return data


def load_subs():
    with open("utils/tidy_conf/data/subs.yml", "r") as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data
