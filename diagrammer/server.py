from localstack.http import Request
from localstack.http.dispatcher import Handler, ResultValue
from diagrammer.diagrammer import Diagrammer


class RequestHandler(Handler):
    def on_get(self, request: Request):
        return self.__call__(request)

    def __call__(self, request: Request, **kwargs) -> ResultValue:
        result = handle_diagram_request() or {}
        return result


def handle_diagram_request():
    diagrammer = Diagrammer()
    return diagrammer.diagram_instance()