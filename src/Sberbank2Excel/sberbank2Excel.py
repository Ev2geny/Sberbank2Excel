"""
Entry point for Sberbank2Excel package.
It runs either CLI or GUI depending on whether command line arguments are provided.
"""

import sys

from Sberbank2Excel import sberbankPDF2Excel, sberbankPDF2ExcelGUI


def main():
    
    # CLI path
    if len(sys.argv) > 1:
        sberbankPDF2Excel.main()
    else:
        # no arguments - start GUI
        sberbankPDF2ExcelGUI.main()


if __name__ == "__main__":
    main()