from inspect import signature
from paddleocr import PaddleOCR
print('PaddleOCR class:', PaddleOCR)
print('PaddleOCR.__init__ signature:', signature(PaddleOCR.__init__))
print('PaddleOCR.predict signature:')
try:
    print(signature(PaddleOCR.predict))
except Exception as e:
    print('could not inspect predict:', e)

# inspect ocr method signature as well
print('\nPaddleOCR.ocr signature:')
try:
    print(signature(PaddleOCR.ocr))
except Exception as e:
    print('could not inspect ocr:', e)

# also list parameters of ocr method if present
print('\nPaddleOCR methods containing ocr:')
for n in dir(PaddleOCR):
    if 'ocr' in n.lower():
        print(' -', n)
