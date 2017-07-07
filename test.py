
from restli import RestliSerializer, RESTLI_V2


V1_REQUEST = {
	'q': 'guided',
	"myFloat": 0.1234987,
	'facets': ['company','network'],
	'selections':[
		{
			'facet': 'company',
			'values': ['1337','439']
		},
		{
			'facet': 'network',
			'values': ['F', 'S']
		}
	],
	'keywords': 'software engineer'
}

V2_REQUEST = {
	"count": 12,
	"myFloat": 0.1234987,
	"emptyDict": {},
	"searchContext": {
		"locale": "en_US",
		"doSpellCheck": "false"
	},
	"fields": {
		"hitInfo": {
			"com.frankieliu.Profile": {
				"firstName": 1,
				"maidenName": 1,
				"lastName": 1
			}
		},
		"type": 1,
		"id": 1,
		"snippets": 1
	},
	"baseSearchParams": {
		"keywords": "software engineer",
		"tracking": {
			"searchId": "12345",
			"searchType": "people",
			"searchOrigin": "FACETS"
		},
		"viewerId": "1234567890123"
	},
	"searchParams": {
		"facetSpecs": [
			{
				"facet": "network",
				"spec": {
					"max": 5,
					"min": 1
				}
			},
			{
				"facet": "company",
				"spec": {
					"max": 5,
					"min": 1
				}
			}
		]
	},
	"metadataFields": {
		"facetContainers": {
			"$*": {
				"facetType": 1,
				"facetValues": {
					"$*": {
						"displayValue": 1,
						"value": 1,
						"isSelected": 1
					}
				}
			}
		},
		"resultComponents": {
			"$*": {
				"position": 1,
				"component": {
					"com.frankieliu.search.Suggestions": 1,
					"com.frankieliu.search.Component": 1
				}
			}
		}
	}
}

def test_serialize_v1():
	serializer = RestliSerializer()
	return serializer.serialize(V1_REQUEST)


def test_serialize_v2():
	serializer = RestliSerializer(version=RESTLI_V2)
	return serializer.serialize(V2_REQUEST)


def test_parse_v1(input):
	serializer = RestliSerializer()
	return serializer.parse(input)


def test_parse_v2(input):
	serializer = RestliSerializer(version=RESTLI_V2)
	return serializer.parse(input)
