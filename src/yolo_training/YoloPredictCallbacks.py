import os

from ultralytics import YOLO
from ultralytics.models.yolo.detect import DetectionPredictor

from src.dataset_manager.Picsellia import Picsellia


class YoloPredictCallbacks:

    def __init__(self, pics: Picsellia) -> None:
        """
        Initialize with a Picsellia instance.

        :param pics: A Picsellia instance used to interact with the dataset and experiment.
        """
        self.__pics: Picsellia = pics

    def apply_callbacks(self, model: YOLO) -> None:
        """
        Add a callback on the 'on_predict_batch_end' event to upload the evaluation of the predictions to Picsellia
        :param model: YOLO model to add the callback to
        :return:
        """
        model.add_callback("on_predict_batch_end", self.__send_evaluation_on_batch_end)

    def __send_evaluation_on_batch_end(self, predictor: DetectionPredictor) -> None:
        dataset = self.__pics.dataset
        experiment = self.__pics.experiment
        for item in predictor.results:
            detected_class_item_count = item.boxes.cls.shape[0]
            boxes = []
            for class_index in range(detected_class_item_count):
                class_id = int(item.boxes.cls[class_index])
                box = [int(i) for i in item.boxes.xywh[class_index].tolist()]
                box[0] = box[0] - box[2] // 2
                box[1] = box[1] - box[3] // 2
                label = dataset.get_label(item.names[class_id])
                conf = float(item.boxes.conf[class_index])
                box.append(label)
                box.append(conf)
                boxes.append(tuple(box))
            img = os.path.splitext(os.path.basename(item.path))[0]
            asset = dataset.find_asset(id=img)
            experiment.add_evaluation(asset, rectangles=boxes)

            print(f"Asset {img} evaluation uploaded")
