"""
Entry point for Sberbank2Excel package.
It runs either CLI or GUI depending on whether command line arguments are provided.
"""

import sys

def main():
    
    # CLI path
    if len(sys.argv) > 1:
        
        from Sberbank2Excel import sberbankPDF2Excel
        
        sberbankPDF2Excel.main()
    else:
        # GUI path
        # importing here to avoid unnecessary GUI dependencies for CLI users
        # this would solve issue 74
        # https://github.com/Ev2geny/Sberbank2Excel/issues/74
        from Sberbank2Excel import sberbankPDF2ExcelGUI
        
        sberbankPDF2ExcelGUI.main()


if __name__ == "__main__":
    main()