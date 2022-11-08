import collections
import sys
import time
import cv2
import numpy as np
from openvino.runtime import Core
sys.path.append("../utils")

# this class is used to detect objects in an image using the OpenVINO toolkit
class ObjectDetection:
    def __init__(self, treshold=0.6):
        self.base_model_dir = "model"
        self.model_name = "ssdlite_mobilenet_v2"
        self.precision = "FP16"
        self.converted_model_path = f"model/public/{self.model_name}/{self.precision}/{self.model_name}.xml"

        self.ie_core = Core()
        self.model = self.ie_core.read_model(model=self.converted_model_path)
        self.compiled_model = self.ie_core.compile_model(model=self.model, device_name="CPU")
        self.input_layer = self.compiled_model.input(0)
        self.output_layer = self.compiled_model.output(0)
        self.height, self.width = list(self.input_layer.shape)[1:3]
        self.input_layer.any_name, self.output_layer.any_name

        self.treshold = treshold

        self.classes = [
            "background", "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train",
            "truck", "boat", "traffic light", "fire hydrant", "street sign", "stop sign",
            "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant",
            "bear", "zebra", "giraffe", "hat", "backpack", "umbrella", "shoe", "eye glasses",
            "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite",
            "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle",
            "plate", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
            "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
            "couch", "potted plant", "bed", "mirror", "dining table", "window", "desk", "toilet",
            "door", "tv", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven",
            "toaster", "sink", "refrigerator", "blender", "book", "clock", "vase", "scissors",
            "teddy bear", "hair drier", "toothbrush", "hair brush"
        ]

        self.colors = cv2.applyColorMap(
            src=np.arange(0, 255, 255 / len(self.classes), dtype=np.float32).astype(np.uint8),
            colormap=cv2.COLORMAP_RAINBOW,
        ).squeeze()

    def process_results(self, frame, results, thresh=0.6):
        # size of the original frame
        h, w = frame.shape[:2]
        # results is a tensor [1, 1, 100, 7]
        results = results.squeeze()
        boxes = []
        labels = []
        scores = []
        for _, label, score, xmin, ymin, xmax, ymax in results:
            boxes.append(
                tuple(map(int, (xmin * w, ymin * h, (xmax - xmin) * w, (ymax - ymin) * h)))
            )
            labels.append(int(label))
            scores.append(float(score))

        indices = cv2.dnn.NMSBoxes(
            bboxes=boxes, scores=scores, score_threshold=thresh, nms_threshold=0.6
        )

        if len(indices) == 0:
            return []

        return [(labels[idx], scores[idx], boxes[idx]) for idx in indices.flatten()]


    def draw_boxes(self, frame, boxes):
        for label, score, box in boxes:
            # choose color for the label
            color = tuple(map(int, self.colors[label]))
            # draw box
            x2 = box[0] + box[2]
            y2 = box[1] + box[3]
            cv2.rectangle(img=frame, pt1=box[:2], pt2=(x2, y2), color=color, thickness=3)

            # draw label name inside the box
            cv2.putText(
                img=frame,
                text=f"{self.classes[label]} {score:.2f}",
                org=(box[0] + 10, box[1] + 30),
                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                fontScale=frame.shape[1] / 1000,
                color=color,
                thickness=1,
                lineType=cv2.LINE_AA,
            )
        return frame

    def human_readable_boxes(self, boxes):
        return [
            (
                self.classes[label],
                score,
                (xmin, ymin, xmax, ymax),
            )
            for label, score, (xmin, ymin, xmax, ymax) in boxes
        ]



    def detect(self, frame):

        scale = 1280 / max(frame.shape)
        if scale < 1:
            frame = cv2.resize(
                src=frame,
                dsize=None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_AREA,
            )

        input_img = cv2.resize(
            src=frame, dsize=(self.width, self.height), interpolation=cv2.INTER_AREA
        )

        input_img = input_img[np.newaxis, ...]
        results = self.compiled_model([input_img])[self.output_layer]
        boxes = self.process_results(frame=frame, results=results, thresh=self.treshold)
        frame = self.draw_boxes(frame=frame, boxes=boxes)


        return frame, self.human_readable_boxes(boxes), boxes



