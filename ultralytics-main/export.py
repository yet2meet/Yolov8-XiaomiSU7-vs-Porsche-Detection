from ultralytics import YOLO

if __name__ == "__main__":
    pth_path = r"F:\SD\sd-webui-aki-v4.8\sd-webui-aki-v4.8\runs\detect\train5\weights\best.pt"
    # Load a model
    # model = YOLO('yolov8n.pt')  # load an official model
    model = YOLO(pth_path)  # load a custom trained model

    # Export the model
    model.export(format='onnx', opset=11, dynamic=True)