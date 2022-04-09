# coding: utf-8

import flask_restful

from ow import api, app, resources

# we always want pretty json
flask_restful.representations.json.settings = {"indent": 4}
api.app.url_map.strict_slashes = False


api.add_resource(resources.Index, "/")

api.add_resource(resources.Status, "/v0/status")

api.add_resource(resources.Job, "/v0/jobs/", "/v0/jobs/<int:id>/", endpoint=str("jobs"))


@app.errorhandler(Exception)
def error_handler(exception):
    """
    log exception
    """
    app.logger.exception("")
