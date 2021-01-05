from unittest import TestCase
from unittest import main
from new_build.tws_clients import HistoricalDataExtractor
import os


class TestHistoricalDataExtractor(TestCase):

    @classmethod
    def setUpClass(cls):
        tickers = [123, 3434]
        cls.extractor = HistoricalDataExtractor(tickers)

    def setup(self):
        pass

    def test_create_data_dump(self):
        ticker = 123
        data = {'bar_data': [{'key_1': 'value_1', 'key_2': 'value_2'}],
                'meta_data': {'meta_key': 'meta_value'}}
        target_file = os.path.dirname(os.path.dirname(__file__))
        print(f'Target file: {target_file}')
        self.extractor.create_data_dump()


if __name__ == '__main__':
    main()
