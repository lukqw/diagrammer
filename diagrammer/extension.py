import logging

from localstack.extensions.api import Extension, http
from localstack.services.internal import get_internal_apis
from localstack.logging.setup import setup_logging

setup_logging()

LOG = logging.getLogger(__name__)

class Diagrammer(Extension):
    name = "diagrammer"

    def on_platform_ready(self):
        LOG.info("diagrammer: extension is loaded")

    def update_gateway_routes(self, router: http.Router[http.RouteHandler]):
        from diagrammer.server import RequestHandler
        from diagrammer.config import HANDLER_PATH

        LOG.info("diagrammer: adding routes to activate extension")
        endpoint = RequestHandler()
        get_internal_apis().add(HANDLER_PATH, endpoint, methods=["GET"])

