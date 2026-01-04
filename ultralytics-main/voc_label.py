import xml.etree.ElementTree as ET
import os
from os import getcwd
 
sets = ['train', 'val', 'test']
classes = ['su7','other']
abs_path = os.getcwd()
print(abs_path)
 
 
def convert(size, box):
    dw = 1. / (size[0])
    dh = 1. / (size[1])
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return x, y, w, h
 
 
def convert_annotation(image_id):
    xml_path = f'data/Annotations/{image_id}.xml'
    if not os.path.exists(xml_path):
        alt_xml_path = f'data/Annotations/{image_id.strip()}.xml'
        if not os.path.exists(alt_xml_path):
            print(f"警告: 找不到注释文件 {xml_path}")
            return
        else:
            xml_path = alt_xml_path
            image_id = image_id.strip()
        
    try:
        in_file = open(xml_path, encoding='UTF-8')
        out_file = open(f'data/labels/{image_id}.txt', 'w')
        tree = ET.parse(in_file)
        root = tree.getroot()
    except Exception as e:
        print(f"处理文件 {xml_path} 时出错: {e}")
        return
    size = root.find('size')
    if size is None:
        print(f"警告: {xml_path} 中找不到size元素")
        in_file.close()
        out_file.close()
        return
        
    width_elem = size.find('width')
    height_elem = size.find('height')
    if width_elem is None or height_elem is None:
        print(f"警告: {xml_path} 中找不到宽度或高度元素")
        in_file.close()
        out_file.close()
        return
        
    try:
        w = int(width_elem.text)
        h = int(height_elem.text)
    except (ValueError, TypeError) as e:
        print(f"警告: {xml_path} 中宽度或高度值无效: {e}")
        in_file.close()
        out_file.close()
        return
    for obj in root.iter('object'):
        # 检查object元素是否包含必要的子元素
        difficult_elem = obj.find('difficult')
        name_elem = obj.find('name')
        
        # 如果缺少必要元素，跳过此object
        if name_elem is None:
            print(f"警告: {xml_path} 中的object缺少name元素")
            continue
            
        # 获取类别名称
        cls = name_elem.text
        
        # 处理difficult标签，如果不存在则默认为0
        difficult = '0'
        if difficult_elem is not None:
            difficult = difficult_elem.text
        
        # 检查类别是否在预定义列表中，以及是否标记为difficult
        try:
            if cls not in classes or int(difficult) == 1:
                continue
        except ValueError:
            print(f"警告: {xml_path} 中的difficult值无效: {difficult}")
            if cls not in classes:
                continue
        cls_id = classes.index(cls)
        
        # 检查边界框元素
        xmlbox = obj.find('bndbox')
        if xmlbox is None:
            print(f"警告: {xml_path} 中的object缺少bndbox元素")
            continue
            
        # 检查边界框坐标
        xmin_elem = xmlbox.find('xmin')
        xmax_elem = xmlbox.find('xmax')
        ymin_elem = xmlbox.find('ymin')
        ymax_elem = xmlbox.find('ymax')
        
        if None in (xmin_elem, xmax_elem, ymin_elem, ymax_elem):
            print(f"警告: {xml_path} 中的bndbox缺少坐标元素")
            continue
            
        try:
            b1 = float(xmin_elem.text)
            b2 = float(xmax_elem.text)
            b3 = float(ymin_elem.text)
            b4 = float(ymax_elem.text)
            
            # 标注越界修正
            if b2 > w:
                print(f"警告: {xml_path} 中的xmax值 {b2} 超出图像宽度 {w}，已修正")
                b2 = w
            if b4 > h:
                print(f"警告: {xml_path} 中的ymax值 {b4} 超出图像高度 {h}，已修正")
                b4 = h
            if b1 < 0:
                print(f"警告: {xml_path} 中的xmin值 {b1} 小于0，已修正")
                b1 = 0
            if b3 < 0:
                print(f"警告: {xml_path} 中的ymin值 {b3} 小于0，已修正")
                b3 = 0
                
            # 检查边界框是否有效
            if b1 >= b2 or b3 >= b4:
                print(f"警告: {xml_path} 中的边界框无效: xmin={b1}, xmax={b2}, ymin={b3}, ymax={b4}")
                continue
                
            b = (b1, b2, b3, b4)
            bb = convert((w, h), b)
            out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
        except (ValueError, TypeError) as e:
            print(f"警告: {xml_path} 中的边界框坐标值无效: {e}")
            continue
 
 
wd = getcwd()

# 统计变量
total_images = 0
processed_images = 0
warning_count = 0

for image_set in sets:
    if not os.path.exists('data/labels/'):
        os.makedirs('data/labels/')
    
    # 读取图像ID列表
    image_ids_path = f'data/ImageSets/{image_set}.txt'
    if not os.path.exists(image_ids_path):
        print(f"警告: 找不到图像ID文件 {image_ids_path}")
        warning_count += 1
        continue
        
    image_ids = open(image_ids_path).read().strip().split('\n')
    list_file = open(f'data/{image_set}.txt', 'w')
    
    set_total = len(image_ids)
    set_processed = 0
    total_images += set_total
    
    print(f"处理数据集 {image_set}，共有 {set_total} 个图像ID")
    
    for image_id in image_ids:
        # 检查图像文件是否存在，处理可能包含空格和括号的文件名
        image_path = os.path.join(abs_path, 'data', 'images', f"{image_id}.jpg")
        if not os.path.exists(image_path):
            # 尝试查找其他可能的文件名格式
            alt_image_path = os.path.join(abs_path, 'data', 'images', f"{image_id.strip()}.jpg")
            if not os.path.exists(alt_image_path):
                print(f"警告: 找不到图像文件 {image_path}")
                warning_count += 1
                continue
            else:
                image_path = alt_image_path
                
        list_file.write(f"{image_path}\n")
        convert_annotation(image_id.strip())
        set_processed += 1
    
    processed_images += set_processed
    print(f"数据集 {image_set} 处理完成，成功处理 {set_processed}/{set_total} 个图像")
    list_file.close()

# 打印总结信息
print("\n处理完成汇总:")
print(f"总图像数: {total_images}")
print(f"成功处理图像数: {processed_images}")
print(f"警告数: {warning_count}")
print(f"成功率: {processed_images/total_images*100:.2f}% 如果成功率较低，请检查文件名格式和路径是否正确")
print("标签文件已保存到 data/labels/ 目录")
print("数据集文件已保存到 data/ 目录下的 train.txt, val.txt, test.txt")