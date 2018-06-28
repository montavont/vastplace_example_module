# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.utils import OperationalError
from django.apps import AppConfig

VASTPLACE_EXAMPLE_TYPE = "vastplace_example"

class VastplaceExampleConfig(AppConfig):
    name = 'experiments.vastplace_example_module'
    def ready(self):
        from campaignfiles.models import SourceType
        try:
            SourceType.objects.get_or_create(sourceType = VASTPLACE_EXAMPLE_TYPE, module = "experiments.vastplace_example_module", parserClass = "csv_parser")
        except OperationalError:
            print "OperationalError while importing"
            pass

