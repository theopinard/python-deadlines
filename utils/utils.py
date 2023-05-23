import yaml

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader, Dumper

from yaml.representer import SafeRepresenter

_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


def dict_representer(dumper, data):
    return dumper.represent_dict(data.iteritems())


def dict_constructor(loader, node):
    return dict(loader.construct_pairs(node))


Dumper.add_representer(dict, dict_representer)
Loader.add_constructor(_mapping_tag, dict_constructor)

Dumper.add_representer(str, SafeRepresenter.represent_str)


def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items()
        )

    OrderedDumper.add_representer(dict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


def pretty_print(header, conf, tba=None, expired=None):
    """Print order of conferences

    Args:
        header (_type_): Header for print
        conf (_type_): conferences
        tba (_type_, optional): tba conferences. Defaults to None.
        expired (_type_, optional): expired conferences. Defaults to None.
    """
    print(header)
    for data in [conf, tba, expired]:
        if data is not None:
            for q in data:
                print(q["cfp"], " - ", q["title"])
            print("\n")
