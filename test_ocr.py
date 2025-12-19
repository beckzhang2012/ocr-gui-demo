import sys
import os
import paddleocr

print('Testing PaddleOCR initialization...')
print('PaddleOCR version:', paddleocr.__version__)

try:
    # 测试基本的 PaddleOCR 初始化
    ocr = paddleocr.PaddleOCR(
        use_angle_cls=True,
        use_gpu=False,
        lang='ch',
        det_model_dir='models/det/ch',
        rec_model_dir='models/rec/ch',
        cls_model_dir='models/cls'
    )
    print('✓ PaddleOCR initialized successfully!')
    
    print('\nTesting OCR recognition on a sample image...')
    # 尝试识别一个简单的图像
    if os.path.exists('test_imgs/sample.jpg'):
        result = ocr.ocr('test_imgs/sample.jpg')
        print('✓ OCR recognition completed!')
        print('Result:', result)
    else:
        print('Sample image not found, skipping recognition test.')
        
except Exception as e:
    print('✗ Error:', str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('\nAll tests passed!')
sys.exit(0)