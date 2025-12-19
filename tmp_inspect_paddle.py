import os
import paddleocr.tools.infer.utility as utility

print('Utility module path:', utility.__file__)
print('\n--- Functions in utility ---')
print([f for f in dir(utility) if not f.startswith('_')])

# 查看 create_predictor 函数的源代码
import inspect
print('\n--- Source code of create_predictor ---')
print(inspect.getsource(utility.create_predictor))

# 查看 TextDetector 类
import paddleocr.tools.infer.predict_det as predict_det
print('\n--- TextDetector class ---')
print(inspect.getsource(predict_det.TextDetector))