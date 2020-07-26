from unittest import TestCase


class Test(TestCase):
    def test_no_exception_when_converting_dlinnaya_vipiska(self):
        from core.sberbankPDFtext2Excel import sberbankPDFtext2Excel
        try:
            sberbankPDFtext2Excel(".\\Example_input_and_output_files\\testovaya_vipiska_po_karte_dlinnaya.txt")
        except Exception:
            self.fail("sberbankPDFtext2Excel raised exception unexpectedly")

    def test_no_exception_when_converting_primer_dlya_soobsheniya_ob_oshibkah(self):
        from core.sberbankPDFtext2Excel import sberbankPDFtext2Excel
        try:
            sberbankPDFtext2Excel(".\\Example_input_and_output_files\\primer_dlya_soobsheniya_ob_oshibkah.txt")
        except Exception:
            self.fail("sberbankPDFtext2Excel raised exception unexpectedly")

    def test_correct_exception_when_converting_testovaya_vipiska_po_karte_dlinnaya_s_oshibkoy(self):
        from core.sberbankPDFtext2Excel import sberbankPDFtext2Excel
        from core.exceptions import SberbankPDFtext2ExcelError
        #pass
        self.assertRaises(SberbankPDFtext2ExcelError,
                          sberbankPDFtext2Excel,
                          ".\\Example_input_and_output_files\\testovaya_vipiska_po_karte_dlinnaya_s_oshibkoy.txt")



