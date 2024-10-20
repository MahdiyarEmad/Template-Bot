import discord, json


class ACL:
    def __init__(self, path: str):
        with open(path) as f:
            self.acl = json.load(f)