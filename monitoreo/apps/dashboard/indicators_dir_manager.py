import os

from django.conf import settings


class IndicatorsDirManager:
    base_dir = os.path.join(settings.MEDIA_ROOT, 'indicator_files')

    def get_network_indicators_dir(self):
        os.makedirs(self.base_dir, exist_ok=True)
        return self.base_dir

    def get_node_indicators_dir(self):
        return self._get_indicator_dir('nodes')

    def get_federator_indicators_dir(self):
        return self._get_indicator_dir('federator-nodes')

    def _get_indicator_dir(self, indic):
        dst_dir = os.path.join(self.base_dir, indic)
        os.makedirs(dst_dir, exist_ok=True)
        return dst_dir
