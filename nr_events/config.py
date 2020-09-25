# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CIS UCT Prague.
#
# CIS theses repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

from __future__ import absolute_import, print_function

from invenio_records_rest.utils import allow_all

RECORDS_DRAFT_ENDPOINTS = {
    'events': {
        'draft': 'draft-events',

        'pid_type': 'nusl',
        'pid_minter': 'nusl',
        'pid_fetcher': 'nusl',
        'default_endpoint_prefix': True,
        'max_result_window': 500000,
        'search_index': 'events',  # TODO: nestáhl se sám, podívat se na to

        'record_class': 'nr_events.record:PublishedEventRecord',

        'publish_permission_factory_imp': allow_all,  # TODO: change this !!!
        'unpublish_permission_factory_imp': allow_all,
        'edit_permission_factory_imp': allow_all,
        'default_media_type': 'application/json',
        # 'indexer_class': CommitingRecordIndexer,

    },
    'draft-events': {
        'pid_type': 'dnusl',
    }
}

FILTERS = {
}

POST_FILTERS = {
}

RECORDS_REST_FACETS = {
}

RECORDS_REST_SORT_OPTIONS = {
}

RECORDS_REST_DEFAULT_SORT = {
}

"""Set default sorting options."""
