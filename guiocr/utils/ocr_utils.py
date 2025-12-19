# -*- coding:utf-8 -*-
"""
基于paddleocr进行OCR识别、版面分析
耗时较多，用于工作线程与主界面线程分离

Author: ZhangSY
Created time:2021/12/1 20:33
"""
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage

from paddleocr import PaddleOCR
# 兼容不同 paddleocr 版本：有些版本未在顶级导出 draw_ocr 等函数
try:
    from paddleocr import draw_ocr
except Exception:
    draw_ocr = None

try:
    from paddleocr import PPStructure, draw_structure_result, save_structure_res
except Exception:
    PPStructure = None
    try:
        from paddleocr.ppstructure import draw_structure_result, save_structure_res
    except Exception:
        draw_structure_result = None
        save_structure_res = None

# 显示结果
from PIL import Image, ImageDraw, ImageFont
import os


class OCR_qt(QObject):
    sendResult = pyqtSignal(list)

    def __init__(self, parent=None, use_gpu: bool = False, use_angle_cls: bool = True):
        super(OCR_qt, self).__init__(parent)
        self.img_path = ""
        self.use_angle = use_angle_cls
        self.cls = True
        self.default_lan = "ch"
        self.result = []
        self.ocrinfer = None
        self.use_gpu = use_gpu
        self.use_paddlex = False  # 禁用 PaddleX 相关功能，避免模型文件缺失错误



    def set_task(self, img_path='./imgs/11.jpg', use_angle=True, cls=True, lan="ch", load=True, regions=None):
        self.img_path = img_path
        self.use_angle = use_angle
        self.cls = cls
        self.default_lan = lan
        self.regions = regions

        if load:
            print("加载模型......")
            # 使用本地模型路径，避免系统路径问题
            params = dict(
                use_angle_cls=use_angle,  # PaddleOCR 2.x 使用 use_angle_cls
                use_gpu=0,  # 禁用 GPU
                lang=lan,
                det_model_dir='models/det/ch',  # PaddleOCR 2.x 使用 det_model_dir
                rec_model_dir='models/rec/ch',  # PaddleOCR 2.x 使用 rec_model_dir
                cls_model_dir='models/cls',  # PaddleOCR 2.x 使用 cls_model_dir
                enable_mkldnn=False
            )

            # Try to initialize PaddleOCR; if it complains about unknown args, remove them and retry
            while True:
                try:
                    self.ocrinfer = PaddleOCR(**params)
                    break
                except ValueError as e:
                    msg = str(e)
                    if "Unknown argument:" in msg:
                        name = msg.split("Unknown argument:")[-1].strip()
                        if name in params:
                            print(f"PaddleOCR: removing unsupported argument '{name}' and retrying...")
                            params.pop(name, None)
                            continue
                    # re-raise if it's not an unknown-argument error we can handle
                    raise

            print("模型加载完成......")

    def start(self):
        if not self.img_path:
            print("No img_path input.")
            return

        # 用于线程启动
        # call ocr without passing deprecated/unsupported kwargs like 'cls'
        self.ocr(self.img_path, regions=self.regions)

    def ocr(self, img_path='./imgs/11.jpg', use_angle=True, cls=True, lan="ch", use_gpu=1, regions=None):
        # 避免使用 PaddleX 功能，直接使用 PaddleOCR 核心识别
        self.img_path = img_path
        self.default_lan = lan

        if regions is None or len(regions) == 0:
            # 全图识别
            try:
                result = self.ocrinfer.ocr(img_path)
            except TypeError:
                result = self.ocrinfer.ocr(img_path)
            self.result = result
        else:
            # 区域识别
            import cv2
            import numpy as np
            from PIL import Image
            import io
            
            image = cv2.imread(img_path)
            result = []
            
            for i, region in enumerate(regions):
                # 裁剪区域
                x1, y1, x2, y2 = region
                cropped = image[y1:y2, x1:x2]
                
                # 将裁剪后的图像转换为临时文件或内存对象
                _, buffer = cv2.imencode('.jpg', cropped)
                img_bytes = io.BytesIO(buffer)
                
                # 使用Pillow读取
                pil_img = Image.open(img_bytes)
                
                # 临时保存到内存
                temp_buffer = io.BytesIO()
                pil_img.save(temp_buffer, format='JPEG')
                temp_buffer.seek(0)
                
                # 对裁剪区域进行OCR
                try:
                    region_result = self.ocrinfer.ocr(temp_buffer)
                except Exception as e:
                    print(f"Error processing region {i}: {e}")
                    region_result = []
                
                # 调整坐标
                if region_result:
                    for line in region_result:
                        if line:
                            # 调整边界框坐标
                            adjusted_box = []
                            for point in line[0]:
                                adjusted_point = (point[0] + x1, point[1] + y1)
                                adjusted_box.append(adjusted_point)
                            # 保持文本和分数不变
                            adjusted_line = [adjusted_box, line[1]]
                            result.append(adjusted_line)
            
            self.result = result

        for line in self.result:
            print(line)
        self.sendResult.emit(self.result)

    def vis_ocr_result(self, save_folder='./output/'):
        image = Image.open(self.img_path).convert('RGB')
        boxes = [line[0] for line in self.result]
        txts = [line[1][0] for line in self.result]
        scores = [line[1][1] for line in self.result]
        # 优先使用 paddleocr 提供的 draw_ocr（新老版本兼容），否则使用 PIL 回退实现
        if draw_ocr is not None:
            im_show = draw_ocr(image, boxes, txts, scores, font_path='./fonts/simfang.ttf')
            im_show = Image.fromarray(im_show)
            os.makedirs(save_folder, exist_ok=True)
            im_show.save(os.path.join(save_folder, 'result_ocr.jpg'))
            return im_show

        # fallback: simple drawing using PIL
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype('./fonts/simfang.ttf', 16)
        except Exception:
            font = None
        for box, txt in zip(boxes, txts):
            pts = [tuple(map(int, p)) for p in box]
            draw.line(pts + [pts[0]], fill=(255, 0, 0), width=2)
            pos = pts[0]
            draw.text(pos, str(txt), fill=(0, 255, 0), font=font)
        os.makedirs(save_folder, exist_ok=True)
        image.save(os.path.join(save_folder, 'result_ocr.jpg'))
        return image


# def ocr(img_path='./imgs/11.jpg',use_angle=True,cls=True, lan="ch"):
#     # Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
#     # 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`
#     ocr = PaddleOCR(use_angle_cls=use_angle, lang=lan)  # need to run only once to download and load model into memory
#     result = ocr.ocr(img_path, cls=cls)
#     for line in result:
#         print(line)
#     return result

# def vis_ocr_result(img_path="",result=None,save_folder = './output/'):
#     image = Image.open(img_path).convert('RGB')
#     boxes = [line[0] for line in result]
#     txts = [line[1][0] for line in result]
#     scores = [line[1][1] for line in result]
#     im_show = draw_ocr(image, boxes, txts, scores, font_path='./fonts/simfang.ttf')
#     im_show = Image.fromarray(im_show)
#     im_show.save(os.path.join(save_folder,'result_ocr.jpg'))
#     return im_show

"""
版面分析
"""
# table_engine = PPStructure(show_log=True)
#
# def structure_analysis(img_path='./table/paper-image.jpg',save_folder = './output/'):
#     img = cv2.imread(img_path)
#     result = table_engine(img)
#     save_structure_res(result, save_folder,os.path.basename(img_path).split('.')[0])
#     for line in result:
#         line.pop('img')
#         print(line)
#     return result
#
# def vis_structure_result(img_path,result,save_folder = './output/'):
#     font_path = './fonts/simfang.ttf' # PaddleOCR下提供字体包
#     image = Image.open(img_path).convert('RGB')
#     im_show = draw_structure_result(image, result,font_path=font_path)
#     im_show = Image.fromarray(im_show)
#     im_show.save(os.path.join(save_folder,'result_struct.jpg'))
#     return im_show

# For Test
if __name__ == "__main__":
    img_path = r'D:\Projects\DemoGUI\test_imgs\00056221.jpg'
    ocrObj = OCR_qt()
    result = ocrObj.ocr(img_path)
    ocrObj.vis_ocr_result()

    # result2 = structure_analysis(img_path)
    # vis_structure_result(img_path,result2)
