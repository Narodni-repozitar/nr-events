import pytest
from marshmallow import ValidationError

from nr_events.marshmallow import EventsMetadataSchemaV1


class TestNameOriginal:
    def test_name_original_1(self, app, db, taxonomy_tree, base_json, base_json_dereferenced,
                             base_event, base_event_dereferenced):
        content = "Česká konference 2020"
        field = "nameOriginal"
        base_json["events"] = [base_event]
        base_json_dereferenced["events"] = [base_event_dereferenced]
        base_json["events"][0][field] = content
        base_json_dereferenced["events"][0][field] = content
        schema = EventsMetadataSchemaV1()
        result = schema.load(base_json)
        assert result == base_json_dereferenced

    def test_name_original_2(self, app, db, taxonomy_tree, base_json, base_json_dereferenced,
                             base_event, base_event_dereferenced):
        # Bad datatype
        content = {
            "cs": "Česká konference 2020",
            "en": "Czech conference 2020"
        }
        field = "nameOriginal"
        base_json["events"] = [base_event]
        base_json_dereferenced["events"] = [base_event_dereferenced]
        base_json["events"][0][field] = content
        base_json_dereferenced["events"][0][field] = content
        schema = EventsMetadataSchemaV1()
        with pytest.raises(ValidationError):
            schema.load(base_json)


class TestNameAlternate:
    def test_name_alternate_1(self, app, db, taxonomy_tree, base_json, base_json_dereferenced,
                              base_event, base_event_dereferenced):
        content = ["Česká konference 2020", "Czech conference 2020"]
        field = "nameAlternate"
        base_json["events"] = [base_event]
        base_json_dereferenced["events"] = [base_event_dereferenced]
        base_json["events"][0][field] = content
        base_json_dereferenced["events"][0][field] = content
        schema = EventsMetadataSchemaV1()
        result = schema.load(base_json)
        assert result == base_json_dereferenced

    def test_name_alternate_2(self, app, db, taxonomy_tree, base_json, base_json_dereferenced,
                              base_event, base_event_dereferenced):
        # wrong data type
        content = {
            "cs": "Česká konference 2020",
            "en": "Czech conference 2020"
        }
        field = "nameAlternate"
        base_json["events"] = [base_event]
        base_json_dereferenced["events"] = [base_event_dereferenced]
        base_json["events"][0][field] = content
        base_json_dereferenced["events"][0][field] = content
        schema = EventsMetadataSchemaV1()
        with pytest.raises(ValidationError):
            schema.load(base_json)


class TestNameUnified:
    def test_name_alternate_1(self, app, db, taxonomy_tree, base_json, base_json_dereferenced,
                              base_event, base_event_dereferenced):
        content = [
            {
                'links': {
                    'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/cze-conference'
                }
            }
        ]
        field = "nameUnified"
        base_json["events"] = [base_event]
        base_json_dereferenced["events"] = [base_event_dereferenced]
        base_json["events"][0][field] = content
        base_json_dereferenced["events"][0][field] = [
            {
                'is_ancestor': False,
                'level': 1,
                'links': {
                    'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/cze-conference'
                },
                'title': {
                    'cs': 'Česká konference',
                    'en': 'Czech conference'
                }
            }
        ]
        schema = EventsMetadataSchemaV1()
        result = schema.load(base_json)
        assert result == base_json_dereferenced

    def test_name_alternate_2(self, app, db, taxonomy_tree, base_json, base_json_dereferenced,
                              base_event, base_event_dereferenced):
        content = [
            {
                'links': {
                    'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/bla'
                }
            }
        ]
        field = "nameUnified"
        base_json["events"] = [base_event]
        base_json_dereferenced["events"] = [base_event_dereferenced]
        base_json["events"][0][field] = content
        base_json_dereferenced["events"][0][field] = content
        schema = EventsMetadataSchemaV1()
        with pytest.raises(ValidationError):
            schema.load(base_json)


class TestDate:
    def test_name_alternate_1(self, app, db, taxonomy_tree, base_json, base_json_dereferenced,
                              base_event, base_event_dereferenced):
        content = "2019-12-23/2019-12-24"
        field = "date"
        base_json["events"] = [base_event]
        base_json_dereferenced["events"] = [base_event_dereferenced]
        base_json["events"][0][field] = content
        base_json_dereferenced["events"][0][field] = content
        schema = EventsMetadataSchemaV1()
        result = schema.load(base_json)
        assert result == base_json_dereferenced

    def test_name_alternate_2(self, app, db, taxonomy_tree, base_json, base_json_dereferenced,
                              base_event, base_event_dereferenced):
        content = "2021-12-23/2021-12-24"
        field = "date"
        base_json["events"] = [base_event]
        base_json_dereferenced["events"] = [base_event_dereferenced]
        base_json["events"][0][field] = content
        base_json_dereferenced["events"][0][field] = content
        schema = EventsMetadataSchemaV1()
        with pytest.raises(ValidationError):
            schema.load(base_json)


class TestLocation:
    def test_location(self, app, db, taxonomy_tree, base_json, base_json_dereferenced,
                      base_event, base_event_dereferenced):
        content = {
            "place": "Praha",
            "country": [
                {
                    "links": {
                        "self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/cz"
                    }
                }
            ]
        }
        field = "location"
        base_json["events"] = [base_event]
        base_json_dereferenced["events"] = [base_event_dereferenced]
        base_json["events"][0][field] = content
        base_json_dereferenced["events"][0][field] = {
            'country': [{
                'code': {
                    'alpha2': 'CZ',
                    'alpha3': 'CZE',
                    'number': '203'
                },
                'is_ancestor': False,
                'level': 1,
                'links': {
                    'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/cz'
                },
                'title': {
                    'cs': 'Česko',
                    'en': 'Czechia'
                }
            }],
            'place': 'Praha'
        }
        schema = EventsMetadataSchemaV1()
        result = schema.load(base_json)
        assert result == base_json_dereferenced

    def test_location_2(self, app, db, taxonomy_tree, base_json, base_json_dereferenced,
                        base_event, base_event_dereferenced):
        content = {
            "place": "Praha",
            "country": [
                {
                    "links": {
                        "self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/bla"
                    }
                }
            ]
        }
        field = "location"
        base_json["events"] = [base_event]
        base_json_dereferenced["events"] = [base_event_dereferenced]
        base_json["events"][0][field] = content
        base_json_dereferenced["events"][0][field] = content
        schema = EventsMetadataSchemaV1()
        with pytest.raises(ValidationError):
            schema.load(base_json)
