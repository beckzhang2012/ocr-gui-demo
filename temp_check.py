import paddleocr
print('paddleocr version:', getattr(paddleocr, '__version__', 'unknown'))
print('exports:', [n for n in dir(paddleocr) if not n.startswith('_')])
print('\nlook for draw function names:')
cands = [n for n in dir(paddleocr) if 'draw' in n.lower()]
print(cands)
