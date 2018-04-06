# -*- coding: utf-8 -*-

from plone.app.layout.viewlets import common as base


class LabelsViewlet(base.ViewletBase):

    @property
    def can_view(self):
        labels = getattr(self.context, 'labels', None)
        if labels:
            return True
        return False
