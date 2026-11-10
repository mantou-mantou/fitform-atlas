"""Negative cases make sure the validator actually rejects incorrect content."""
import copy
import json
import unittest
from pathlib import Path
from validate_content import validate, ROOT


class ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads((ROOT/'data/exercises.json').read_text(encoding='utf-8'))

    def check_mutation(self, mutation, expected):
        doc=copy.deepcopy(self.original)
        mutation(doc)
        errors=validate(doc)
        self.assertTrue(any(expected in message for message in errors), errors)

    def test_original_valid(self):
        self.assertEqual(validate(self.original), [])

    def test_duplicate_id_is_rejected(self):
        self.check_mutation(lambda d:d['exercises'][1].update(id='bench-press'), '重複')

    def test_missing_required_field_is_rejected(self):
        self.check_mutation(lambda d:d['exercises'][0].pop('summary'), '欄位不符')

    def test_unknown_category_is_rejected(self):
        self.check_mutation(lambda d:d['exercises'][0].update(category='arms'), 'category 不在')

    def test_invalid_url_is_rejected(self):
        self.check_mutation(lambda d:d['exercises'][0]['sources'][0].update(url='http://bad.local'), '必須是 HTTPS')

    def test_missing_svg_is_rejected(self):
        self.check_mutation(lambda d:d['exercises'][0].update(illustration='assets/illustrations/no.svg'), 'illustration 必須為')

    def test_too_few_steps_is_rejected(self):
        self.check_mutation(lambda d:d['exercises'][0].update(steps=[{'title':'一','description':'二'}]), '至少 3 筆')


if __name__ == '__main__':unittest.main()
