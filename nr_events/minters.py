# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Persistent identifier minters."""

from __future__ import absolute_import, print_function

from .providers import NREventsIdProvider


def nr_events_id_minter(record_uuid, data):
    """Mint record identifiers.

    This is a minter specific for records.
    With the help of
    :class:`invenio_pidstore.providers.recordid.RecordIdProvider`, it creates
    the PID instance with `rec` as predefined `object_type`.

    Procedure followed: (we will use `control_number` as value of
    `PIDSTORE_nr_id_FIELD` for the simplicity of the documentation.)

    #. If a `control_number` field is already there, a `AssertionError`
    exception is raised.

    #. The provider is initialized with the help of
    :class:`invenio_pidstore.providers.recordid.RecordIdProvider`.
    It's called with default value 'rec' for `object_type` and `record_uuid`
    variable for `object_uuid`.

    #. The new `id_value` is stored inside `data` as `control_number` field.

    :param record_uuid: The record UUID.
    :param data: The record metadata.
    :returns: A fresh `invenio_pidstore.models.PersistentIdentifier` instance.
    """
    pid_field = "control_number"
    assert pid_field not in data
    provider = NREventsIdProvider.create(
        object_type='rec', object_uuid=record_uuid)
    data[pid_field] = provider.pid.pid_value
    return provider.pid
