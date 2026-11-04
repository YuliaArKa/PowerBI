import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('check_observations',ROOT/'tools/check_observations.py')
checker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class ObservationValidation(unittest.TestCase):
    def run_rows(self, rows):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'observations.csv'
            with p.open('w',encoding='utf-8-sig',newline='') as f:
                w=csv.writer(f);w.writerow(checker.FIELDS);w.writerows(rows)
            return checker.validate(p)

    def test_empty_template_is_explicitly_zero_rows(self):
        self.assertEqual(self.run_rows([]),(0,[]))

    def test_real_format_and_missing_value(self):
        # Small input fixtures for validation only; never shipped as report data.
        n,e=self.run_rows([['M','2023-01-01','TEST','100.5','בדיקה',''],['M','2023-02-01','TEST','','בדיקה','']])
        self.assertEqual((n,e),(2,[]))

    def test_duplicate_periods_rejected(self):
        row=['M','2023-01-01','TEST','1','','']
        self.assertTrue(any('duplicate' in e for e in self.run_rows([row,row])[1]))

    def test_ambiguous_date_rejected(self):
        self.assertTrue(any('ISO' in e for e in self.run_rows([['M','01/02/2023','TEST','1','','']])[1]))

    def test_quarter_start_required(self):
        self.assertTrue(any('quarter starts' in e for e in self.run_rows([['Q','2023-02-01','TEST','1','','']])[1]))

    def test_month_start_required(self):
        self.assertTrue(any('first day' in e for e in self.run_rows([['M','2023-02-15','TEST','1','','']])[1]))

    def test_non_finite_numbers_rejected(self):
        for v in ['NaN','inf','-inf','not a number']:
            with self.subTest(v=v):
                self.assertTrue(any('finite decimal' in e for e in self.run_rows([['M','2023-01-01','TEST',v,'','']])[1]))

    def test_mixed_series_frequencies_rejected(self):
        rows=[['M','2023-01-01','TEST','1','',''],['Q','2023-04-01','TEST','2','','']]
        self.assertTrue(any('mix frequencies' in e for e in self.run_rows(rows)[1]))

    def test_concrete_series_code_required(self):
        for code in ['', ' TEST', 'A,B', 'SERIES_<X>']:
            with self.subTest(code=code):
                self.assertTrue(any('SERIES_CODE' in e for e in self.run_rows([['M','2023-01-01',code,'1','','']])[1]))


class CatalogueNormalization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('builder',ROOT/'tools/build_project.py')
        cls.builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.builder)
        cls.temp=tempfile.TemporaryDirectory()
        cls.builder.ROOT=Path(cls.temp.name)
        cls.builder.DATA=Path(cls.temp.name)/'data'
        import shutil
        shutil.copytree(ROOT/'data/source',cls.builder.DATA/'source')
        cls.graphs,cls.maps=cls.builder.normalize()

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_kpi_typo_and_combined_codes_resolved(self):
        codes={m['series_code_id'] for m in self.maps if m['graph_id']=='kpi06'}
        self.assertEqual(codes,{'EM_M_SA','EM_MAL_M_SA','EM_FEM_M_SA'})

    def test_leading_comma_does_not_create_blank_series(self):
        codes={m['series_code_id'] for m in self.maps if m['graph_id']=='kpi07'}
        self.assertEqual(codes,{'WT_NO_FRN_Q_SA','WT_BS_NO_FRN_Q_SA','WT_8_NO_FRN_Q_SA'})

    def test_home_kpi_duplicates_removed(self):
        for graph,n in [('kpi01',3),('kpi02',2),('kpi03',2),('kpi04',3)]:
            self.assertEqual(sum(m['graph_id']==graph for m in self.maps),n)

    def test_wage_raw_and_smoothing_both_preserved(self):
        rows=[m for m in self.maps if m['graph_id']=='g04']
        self.assertEqual(len(rows),2)
        self.assertEqual({m['transform'] for m in rows},{'Raw','MA4Q'})

    def test_no_regional_series_invented(self):
        self.assertFalse(any(m['graph_id'] in {'g25','g26','g27','g28','g29','g30','g31'} for m in self.maps))
        self.assertTrue(any(g['graph_id']=='g25' for g in self.graphs))


if __name__=='__main__':unittest.main()
