
from diagrams.aws import compute, integration, storage, network, management
from typing import Any, List

MappingRelation = List[str]
MappingResultType = tuple[Any, str, str, MappingRelation]  

class MappingResult:

    def __init__(self, symbol, name, arn, relations) -> MappingResultType:
        self.symbol : Any = symbol
        self.name : str = name
        self.arn : str = arn
        self.relations : MappingRelation = relations

class Mapper:

    service_mapping = {
        "Lambda": { 
            "symbol": compute.Lambda, 
            "entities": [
                {
                "name": "Functions", 
                "arn": "FunctionArn"
                }
            ]
        },
        "SNS": { 
            "symbol" : integration.SNS, 
            "entities": [
                {
                "name": "Topics",
                "arn": "TopicArn"
                }
            ]
        },
        "AppSync": {
            "symbol": integration.Appsync,
            "relations": [
                "authorizerUri"
            ],
            "entities": [
                {
                "name": "graphqlApis",
                "arn": "arn"
                }
            ]
        },
        "S3": {
            "symbol": storage.S3,
            "entities": [
                {
                    "name": 'Buckets',
                    "arn": "Name"
                }
            ]
        },
        "APIGateway": {
            "symbol": network.APIGateway,
            "entities": [
                {
                    "name": 'items',
                    "arn": "name"
                }
            ]
        },
        "CloudWatchLogs": {
            "symbol": management.Cloudwatch,
            "entities": [{
                "name": "logGroups",
                "arn": "arn"
            }]
        }
    }


    def _get_kv_from_nested_dict(self, dic, key):
        if type(dic) is not dict:
            return None

        if key in dic:
            return dic[key]
        
        for keys in dic:
            result = self._get_kv_from_nested_dict(dic[keys], key)
            if result:
                return result

    def _safe_get_kv_from_nested_dict(self, dict, key):
        try:
            return self._get_kv_from_nested_dict(dict, key)
        except:
            return 


    def _get_relations_for_entity(self, entity, fields):
        relations = []
        for field in fields:
            relation = self._safe_get_kv_from_nested_dict(entity, field)
            if relation:
                relations.append(relation)
        return relations


    def get_mapping_for_pod_service(self, pod_service: str, description: dict) -> List[MappingResultType]:
        result: List[MappingResultType] = []

        if pod_service in self.service_mapping:
            related_service = self.service_mapping[pod_service]
            symbol = related_service["symbol"]
            entities = related_service["entities"]
            entity_relations_fields = related_service.get("relations")
            for entity in entities:
                entity_name = entity["name"]
                entity_arn = entity["arn"]
                pod_entities = self._safe_get_kv_from_nested_dict(description, entity_name)
                for pod_entity in pod_entities:
                    arn = pod_entity[entity_arn]
                    name = arn.rsplit(':', 1)[-1]
                    
                    relations = self._get_relations_for_entity(pod_entity, entity_relations_fields) if entity_relations_fields else None
                    mappingResult = MappingResult(symbol, name, arn, relations)
                    result.append(mappingResult)

        return result
        