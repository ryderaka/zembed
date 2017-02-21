

def create_json(meta):

    data = {
        "url": meta["url"],
        "title": meta["title"],
        "description": meta["description"],
        "time": meta["time"],
        "image": meta["image"],
        }

    if (meta["author"] or meta['author_url']) != "":
        data["author"] = {
            "name": meta["author"],
            "url": meta["author_url"],
        }
    if (meta["video"] or meta["poster"]) not in ["", None, (None,), ('',), []]:
            data["embed"] = {
                "code": meta["video"],
                "poster": meta["poster"],
            },
    if meta["audio"] != "":
        data["audio"] = meta["audio"],
    return data

