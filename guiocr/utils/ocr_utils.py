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
import glob


class OCR_qt(QObject):
    sendResult = pyqtSignal(list)

    def __init__(self, parent=None):
        super(OCR_qt, self).__init__(parent)
        self.img_path = ""
        self.use_angle = True
        self.cls = True
        self.default_lan = "ch"
        self.result = []
        self.ocrinfer = None



    def set_task(self, img_path='./imgs/11.jpg', use_angle=True, cls=True, lan="ch", load=True):
        self.img_path = img_path
        self.use_angle = use_angle
        self.cls = cls
        self.default_lan = lan

        if load:
            print("加载模型......")
            # Only pass explicit model dirs if they exist and look complete;
            # otherwise let PaddleOCR handle downloading / locating models itself.
            det_dir = f"models/det/{lan}"
            rec_dir = f"models/cls/{lan}"

            if not (os.path.isdir(det_dir) and os.path.exists(os.path.join(det_dir, "inference.yml"))):
                print(f"PaddleOCR: model directory '{det_dir}' missing or incomplete; will not pass det_model_dir (PaddleOCR may download models).")
                det_dir = None
            if not (os.path.isdir(rec_dir) and os.path.exists(os.path.join(rec_dir, "inference.yml"))):
                print(f"PaddleOCR: model directory '{rec_dir}' missing or incomplete; will not pass rec_model_dir (PaddleOCR may download models).")
                rec_dir = None

            params = dict(
                use_angle_cls=use_angle,
                use_gpu=1,
                lang=lan,
            )
            if det_dir:
                params["det_model_dir"] = det_dir
            if rec_dir:
                params["rec_model_dir"] = rec_dir

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
        self.ocr(self.img_path)

    def ocr(self, img_path='./imgs/11.jpg', use_angle=True, cls=True, lan="ch", use_gpu=1):
        self.img_path = img_path
        self.default_lan = lan

        # PaddleOCR.predict no longer accepts 'cls' keyword in newer versions;
        # call without it to avoid TypeError
        try:
            result = self.ocrinfer.ocr(img_path)
        except TypeError:
            # fallback: try with explicit safe kwargs if needed in older versions
            result = self.ocrinfer.ocr(img_path)

        self.result = result
        for line in result:
            print(line)
        self.sendResult.emit(result)

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


class BatchOCRProcessor(QObject):
    """批量OCR处理类"""
    # 信号定义
    progressUpdated = pyqtSignal(int, int)  # 当前进度, 总任务数
    imageProcessed = pyqtSignal(str, list, float)  # 图片路径, 识别结果, 置信度
    imageError = pyqtSignal(str, str)  # 图片路径, 错误信息
    batchComplete = pyqtSignal(dict)  # 完整结果
    sendResult = pyqtSignal(list)

    def __init__(self, parent=None):
        super(BatchOCRProcessor, self).__init__(parent)
        self.image_paths = []
        self.use_angle = True
        self.cls = True
        self.default_lan = "ch"
        self.ocrinfer = None
        self.is_running = False

    def set_task(self, image_paths, use_angle=True, cls=True, lan="ch"):
        """设置批量任务"""
        self.image_paths = image_paths
        self.use_angle = use_angle
        self.cls = cls
        self.default_lan = lan
        self._load_model()

    def _load_model(self):
        """加载OCR模型"""
        print("加载批量处理模型......")
        det_dir = f"models/det/{self.default_lan}"
        rec_dir = f"models/cls/{self.default_lan}"

        if not (os.path.isdir(det_dir) and os.path.exists(os.path.join(det_dir, "inference.yml"))):
            print(f"PaddleOCR: model directory '{det_dir}' missing or incomplete; will not pass det_model_dir (PaddleOCR may download models).")
            det_dir = None
        if not (os.path.isdir(rec_dir) and os.path.exists(os.path.join(rec_dir, "inference.yml"))):
            print(f"PaddleOCR: model directory '{rec_dir}' missing or incomplete; will not pass rec_model_dir (PaddleOCR may download models).")
            rec_dir = None

        params = dict(
            use_angle_cls=self.use_angle,
            use_gpu=1,
            lang=self.default_lan,
        )
        if det_dir:
            params["det_model_dir"] = det_dir
        if rec_dir:
            params["rec_model_dir"] = rec_dir

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

        print("批量处理模型加载完成......")

    def start(self):
        """开始批量处理"""
        self.is_running = True
        self.process_batch()

    def stop(self):
        """停止批量处理"""
        self.is_running = False

    def process_batch(self):
        """处理批量任务"""
        total = len(self.image_paths)
        results = {}
        errors = {}

        for idx, img_path in enumerate(self.image_paths):
            if not self.is_running:
                break

            # 更新进度
            self.progressUpdated.emit(idx + 1, total)

            try:
                # 执行OCR识别
                result = self.ocrinfer.ocr(img_path)
                
                # 计算平均置信度
                if result:
                    scores = [line[1][1] for line in result]
                    avg_confidence = sum(scores) / len(scores)
                else:
                    avg_confidence = 0.0

                # 发送处理结果
                self.imageProcessed.emit(img_path, result, avg_confidence)
                results[img_path] = {"result": result, "confidence": avg_confidence}

            except Exception as e:
                error_msg = str(e)
                print(f"处理图片 {img_path} 时出错: {error_msg}")
                self.imageError.emit(img_path, error_msg)
                errors[img_path] = error_msg

        # 发送完成信号
        final_result = {
            "results": results,
            "errors": errors,
            "total": total,
            "success": len(results),
            "failed": len(errors)
        }
        self.batchComplete.emit(final_result)
        self.is_running = False


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
