from flask import current_app

from app.container import Container


def get_container() -> Container:
    return current_app.extensions["container"]