import logging
import base64
import uuid
from diagrams import Diagram
from localstack_ext.bootstrap import pods_client
from typing import List

from diagrammer.mapper import Mapper, MappingResultType

LOG = logging.getLogger(__name__)

class Diagrammer:

    def __init__(self):
        self.mapper = Mapper()

    def embed_svg(self, diagram):
        from lxml import etree
        from base64 import b64encode
        import os

        svg = etree.fromstring(diagram)

        # Mention: must give svg namespace
        tag_image = './/{http://www.w3.org/2000/svg}image'
        tag_href = '{http://www.w3.org/1999/xlink}href'

        for img in svg.findall(tag_image):
            rsc = img.attrib.get(tag_href, None)

            # Only process local image files
            if rsc is None or not os.path.exists(rsc):
                continue

            # Only support some pre-define type
            ext = rsc.split('.')[-1]
            if ext not in ['png','jpg']:
                continue

            # Use base64 to embed the image resource
            with open(rsc, 'rb') as data:
                b = data.read()
                code = b64encode(b)
                img.attrib[tag_href] = 'data:image/{};base64,{}'.format(ext, code.decode())

        # Write back to the svg file
        elemtree = etree.ElementTree(svg)
        root = elemtree.getroot()
        root = etree.tostring(root)
        return root

    def _describe_current_pod(self):
        self.pod_name = str(uuid.uuid4())
        pods_client.commit_state(pod_name=self.pod_name)
        result = pods_client.get_version_metamodel(pod_name=self.pod_name, version=-1)
        return result

    def _cleanup(self):
        pods_client.delete_pod(pod_name=self.pod_name, remote=False)

    def diagram_instance(self):
        LOG.info("diagramming current localstack instance")

        pod_description = self._describe_current_pod()

        mappings = []

        with Diagram("", show=False, outformat="svg") as diag:

            for account_id, pod_services in pod_description.items():
                for pod_service in pod_services:
                    result: List[MappingResultType] = self.mapper.get_mapping_for_pod_service(pod_service, pod_services[pod_service])
                    for entry in result:
                        mappings.append(entry)

            drawn_arns = []

            for mapping in mappings:
                if mapping.relations:
                    relatedEntities = []
                    for rel in mapping.relations:
                        for maprel in mappings:
                            if maprel.arn == rel:
                                relatedEntities.append(maprel)
                                drawn_arns.append(maprel.arn)

                    mapping.symbol(mapping.name) >> [relatedEntity.symbol(relatedEntity.name) for relatedEntity in relatedEntities]
                    drawn_arns.append(mapping.arn)
            
            for mapping in mappings:
                if mapping.arn not in drawn_arns:
                    mapping.symbol(mapping.name)


            output = diag.dot.pipe(format="svg")
            embedded_svg = self.embed_svg(output)
            b64output = base64.b64encode(embedded_svg).decode('utf-8')


        self._cleanup()
        return b64output

# diagrammer = Diagrammer()
# diagrammer.diagram_instance()