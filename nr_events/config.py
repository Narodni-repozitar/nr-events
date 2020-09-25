# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CIS UCT Prague.
#
# CIS theses repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

from __future__ import absolute_import, print_function

from elasticsearch_dsl import Q
from invenio_records_rest.facets import terms_filter
from invenio_records_rest.utils import allow_all

RECORDS_DRAFT_ENDPOINTS = {
    'theses': {
        'draft': 'draft-theses',

        'pid_type': 'nusl',
        'pid_minter': 'nusl',
        'pid_fetcher': 'nusl',
        'default_endpoint_prefix': True,
        'max_result_window': 500000,

        'record_class': 'invenio_nusl_theses.record:PublishedThesisRecord',

        'publish_permission_factory_imp': allow_all,  # TODO: change this !!!
        'unpublish_permission_factory_imp': allow_all,
        'edit_permission_factory_imp': allow_all,
        'default_media_type': 'application/json',
        # 'indexer_class': CommitingRecordIndexer,

    },
    'draft-theses': {
        'pid_type': 'dnusl',
        # 'record_class': 'restoration.objects.record.RestorationObjectDraftRecord',
        # 'create_permission_factory_imp':
        #     'restoration.objects.permissions.create_object_permission_impl',
        # 'update_permission_factory_imp':
        #     'restoration.objects.permissions.update_object_permission_impl'
    }
}


# THESES_SEARCH_INDEX = 'invenio_nusl_theses-nusl-theses-v1.0.0'
# THESES_STAGING_SEARCH_INDEX = 'invenio_nusl_theses-nusl-theses-staging-v1.0.0'
# THESES_PID = 'pid(nusl,record_class="invenio_nusl_theses.api:ThesisRecord")'
# THESES_STAGING_JSON_SCHEMA = "https://nusl.cz/schemas/invenio_nusl_theses/nusl-theses-staging
# -v1" \
#                              ".0.0.json"

# DRAFT_ENABLED_RECORDS_REST_ENDPOINTS = {
#     'theses': {
#         'json_schemas': [
#             'invenio_nusl_theses/nusl-common-v1.0.0.json'
#         ],
#         'published_pid_type': 'nusl',
#         'pid_minter': 'nusl',
#         'pid_fetcher': 'nusl',
#         'draft_pid_type': 'dnusl',
#         'draft_allow_patch': True,
#         'max_result_window': 500000,
#
#         'record_marshmallow': ThesisRecordSchemaV1,
#         'metadata_marshmallow': ThesisMetadataSchemaV1,
#
#         'draft_record_class': DraftThesisRecord,
#         'published_record_class': PublishedThesisRecord,
#
#         'publish_permission_factory': thesis_write_permission_factory,
#         'unpublish_permission_factory': thesis_write_permission_factory,
#         'edit_permission_factory': thesis_write_permission_factory,
#         'draft_modify_permission_factory': thesis_write_permission_factory,
#         'draft_read_permission_factory': thesis_write_permission_factory,
#
#         # 'search_class': DebugACLRecordsSearch,
#         # 'indexer_class': CommitingRecordIndexer,
#
#     }
# }


def degree_grantor_filter(field, path=None):
    def inner(values):
        return Q('nested',
                 path="degreeGrantor.ancestors",
                 query=Q("nested",
                         path="degreeGrantor.ancestors.title",
                         query=Q('terms',
                                 **{field: values}
                                 ))
                 )

    return inner


def nested_terms_filter(prefix, field, field_query=None):
    """Create a term filter.

    :param prefix
    :param field: Field name.
    :param field_query
    :returns: Function that returns the Terms query.
    """

    field = prefix + '.' + field

    def inner(values):
        if field_query:
            query = field_query(field)(values)
        else:
            query = Q('terms', **{field: values})
        return Q('nested', path=prefix, query=query)

    return inner


def year_filter(field):
    """Create a term filter.

    :param field: Field name.
    :returns: Function that returns the Terms query.
    """

    def inner(values):
        queries = []
        for value in values:
            queries.append(
                Q('range', **{
                    field: {
                        "gte": value,
                        "lt": int(value) + 1,
                        "format": "yyyy"
                    }
                })
            )
        return Q('bool', should=queries, minimum_should_match=1)

    return inner


def person_filter(field):
    """Create a term filter.

    :param field: Field name.
    :returns: Function that returns the Terms query.
    """

    def inner(values):
        queries = []
        for value in values:
            queries.append(
                Q('term', **{
                    field: value
                })
            )
        return Q('bool', should=queries, minimum_should_match=1)

    return inner


def boolean_filter(field):
    def inner(values):
        queries = []
        for value in values:
            queries.append(
                Q('term', **{
                    field: bool(int(value))
                })
            )
        return Q('bool', should=queries, minimum_should_match=1)

    return inner


FILTERS = {
    'yearAccepted': year_filter('dateAccepted'),
    'language': terms_filter('language.slug'),
    'defended': boolean_filter('defended'),
    'person': person_filter('person.keyword'),
    'subjectKeywords': terms_filter('subjectKeywords'),
    'accessRights': terms_filter('accessRights'),
    'studyField': nested_terms_filter('studyField.title', 'value.keyword'),
    'provider': nested_terms_filter('provider.title', 'value.keyword'),
    'university': degree_grantor_filter('degreeGrantor.ancestors.title.value.keyword'),
    'faculty': degree_grantor_filter('degreeGrantor.ancestors.title.value.keyword'),
    'valid': boolean_filter("invenio_draft_validation.valid"),
    'marshmallow.field': terms_filter("invenio_draft_validation.errors.marshmallow.field"),
    'marshmallow.message': terms_filter(
        "invenio_draft_validation.errors.marshmallow.message.keyword"),
    'jsonschema.field': terms_filter("invenio_draft_validation.errors.jsonschema.field"),
    'jsonschema.message': terms_filter("invenio_draft_validation.errors.jsonschema.message.keyword")
}

POST_FILTERS = {
    'doctype.slug': terms_filter('doctype.slug'),
}

RECORDS_REST_FACETS = {
    'draft-invenio_nusl_theses-nusl-theses-v1.0.0': {
        'aggs': {  # agregace
            # 'yearAccepted': {
            #     "date_histogram": {
            #         "field": "dateAccepted",
            #         "interval": "1y",
            #         "format": "yyyy",
            #         "min_doc_count": 1,
            #         "order": {
            #             "_key": "desc"
            #         }
            #
            #     }
            # },
            'language': {
                'terms': {
                    'field': 'language.slug',
                    'order': {'_count': 'desc'}
                }
            },
            'defended': {
                'terms': {
                    'field': 'defended'
                }
            },
            'doctype.slug': {
                'terms': {
                    'field': 'doctype.slug'
                }
            },
            # 'person': {
            #     'terms': {
            #         'field': 'person.keyword'
            #     }
            # },
            # 'subjectKeywords': {
            #     'terms': {
            #         'field': 'subjectKeywords',
            #         'size': 100
            #     }
            # },
            # 'accessRights': {
            #     'terms': {
            #         'field': 'accessRights'
            #     }
            # },
            # "studyField": {
            #     "nested": {
            #         "path": "studyField.title"
            #     },
            #     "aggs": {
            #         "studyField": {
            #             "terms": {
            #                 "field": "studyField.title.value.keyword",
            #                 "size": 100
            #             }
            #         }
            #     }
            # },
            "provider": {
                "nested": {
                    "path": "provider.title"
                },
                "aggs": {
                    "provider": {
                        "terms": {
                            "field": "provider.title.value.keyword",
                            "size": 100
                        }
                    }
                }
            },
            "valid": {
                'terms': {
                    'field': "invenio_draft_validation.valid"
                }
            },
            "marshmallow.field": {
                "terms": {
                    "field": "invenio_draft_validation.errors.marshmallow.field"
                }
            },
            "marshmallow.message": {
                "terms": {
                    "field": "invenio_draft_validation.errors.marshmallow.message.keyword"
                }
            },
            "jsonschema.field": {
                "terms": {
                    "field": "invenio_draft_validation.errors.jsonschema.field"
                }
            },
            "jsonschema.message": {
                "terms": {
                    "field": "invenio_draft_validation.errors.jsonschema.message.keyword"
                }
            }
        },
        'filters': FILTERS,
        'post_filters': POST_FILTERS
    }
}

RECORDS_REST_SORT_OPTIONS = {
    'draft-invenio_nusl_theses-nusl-theses-v1.0.0': dict(
        byid=dict(
            title=('by id'),
            fields=['-id'],
            default_order='desc',
            order=1,
        ),
        bestmatch=dict(
            title=('Best match'),
            fields=['_score'],
            default_order='desc',
            order=2,
        ),
        mostrecent=dict(
            title=('Most recent'),
            fields=['-_created'],
            default_order='asc',
            order=3,
        ),
    )
}

RECORDS_REST_DEFAULT_SORT = {
    'draft-invenio_nusl_theses-nusl-theses-v1.0.0': {
        'query': 'byid',
        'noquery': 'byid',
    }
}

"""Set default sorting options."""
