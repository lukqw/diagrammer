from localstack.extensions.api import Extension, http, aws, services
from localstack.services.internal import get_internal_apis

import logging
from server import RequestHandler
from config import HANDLER_PATH

LOG = logging.getLogger(__name__)

class MyExtension(Extension):
    name = "diagrammer"

    def on_platform_ready(self):
        LOG.info("diagrammer: extension is loaded")
        print("test")

    def update_gateway_routes(self, router: http.Router[http.RouteHandler]):
        endpoint = RequestHandler()
        get_internal_apis().add(HANDLER_PATH, endpoint, methods=["GET"])

