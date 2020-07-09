from core.sberbankPDFtext2Excel import sberbankPDFtext2Excel
import sys
if len(sys.argv) < 2:
    print('Недостаточно аргументов')
    print(__doc__)
    exit(1)
elif len(sys.argv)==2:
    outputFileName = None
elif len(sys.argv)==3:
    outputFileName=sys.argv[2]

sberbankPDFtext2Excel(sys.argv[1], outputFileName)
