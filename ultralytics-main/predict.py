from ultralytics import YOLO

if __name__ == "__main__":
    pth_path = r"F:\SD\sd-webui-aki-v4.8\sd-webui-aki-v4.8\runs\detect\train5\weights\best.onnx"

    test_path = r"F:\ultralytics-main\detect_test\test1.png"
    # Load a model
    # model = YOLO('yolov8n.pt')  # load an official model
    model = YOLO(pth_path)  # load a custom model

    # Predict with the model
    results = model(test_path, save=True, conf=0.5)  # predict on an image