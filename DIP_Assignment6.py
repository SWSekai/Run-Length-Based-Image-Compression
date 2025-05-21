import cv2
import numpy as np
import os

def rle_compress_2d(img_path, output_file_path):
    """
        對二維數據進行 Run-Length Encoding 壓縮。
    """
    try:
        img = cv2.imread(img_path)
    except Exception as e:
        print(f"影像讀取失敗: {e}")
        return
    
    compressed_data = []
    
    height, width, channels = img.shape
    
    for i in range(channels):
        channel_data = img[:, :, i].flatten()
        compressed_channel_data = rle_compress(channel_data)
        compressed_data.append(compressed_channel_data)
    
    # 寫入壓縮後的影像
    with open(output_file_path, 'wb') as f:
        f.write(height.to_bytes(4, 'big'))
        f.write(width.to_bytes(4, 'big'))
        f.write(channels.to_bytes(4, 'big'))
        
        for channel_data in compressed_data:
            f.write(len(channel_data).to_bytes(4, 'big'))
            for value, count in channel_data:
                f.write(int(value).to_bytes(1, 'big'))
                f.write(int(count).to_bytes(4, 'big'))
    
    print("壓縮完成, 已將壓縮檔案儲存至: ", output_file_path)
    
    ratio = calculate_compression_ratio(img_path, output_file_path)   
    
    return compressed_data, ratio

def rle_compress(data):
    """
        對一維數據進行 Run-Length Encoding 壓縮。
    """
    current_value = data[0]
    compressed_data = []
    count = 1
    
    if data is None:
        print("數據為空")
        return []
    
    for i in range(1, len(data)):
        if data[i] == current_value:
            count += 1
        else:
            compressed_data.append((current_value, count))
            current_value = data[i]
            count = 1
    compressed_data.append((current_value, count))
    
    return compressed_data

def calculate_compression_ratio(original_file_path, compressed_file_path):
    """
        計算壓縮率
    """
    original_size = os.path.getsize(original_file_path)
    compressed_size = os.path.getsize(compressed_file_path)
    
    compression_ratio = round((1-compressed_size / original_size)*100, 2)
    
    print("原始檔案大小: ", original_size, "bytes")
    print("壓縮後檔案大小: ", compressed_size, "bytes")
    print("\n壓縮率: ", compression_ratio, "%")
    
    return compression_ratio

def decompress_image_rle(compressed_file_path, output_file_path):
    """
        解壓縮 Run-Length Encoding 壓縮的影像。
    """
    with open(compressed_file_path, 'rb') as f:
        height = int.from_bytes(f.read(4), 'big')
        width = int.from_bytes(f.read(4), 'big')
        channels = int.from_bytes(f.read(4), 'big')
        
        channels_data = []
        
        for _ in range(channels):
            channel_size = int.from_bytes(f.read(4), 'big')
            channel_data = []
            for _ in range(channel_size):
                value = int.from_bytes(f.read(1), 'big')
                count = int.from_bytes(f.read(4), 'big')
                
                channel_data.append((value, count))
            channels_data.append(rle_decompress(channel_data))
            
        image = np.zeros((height, width, channels), dtype=np.uint8)
        
        # 將壓縮後的數據轉換為影像
        for i in range(channels):
            channel_data = np.array(channels_data[i])
            
            image_channel = channel_data.reshape((height, width))
            image[:, :, i] = image_channel
    
    cv2.imwrite(output_file_path, image)
    print("解壓縮完成, 已將影像儲存至: ", output_file_path)
    
    return image

def rle_decompress(data):
    """
        對一維數據進行 Run-Length Encoding 解壓縮。
    """
    decompress_data = []
    
    for value, count in data:
        decompress_data.extend([value] * count)
    
    return decompress_data

def vertify_decompress(original_file_path, decompressed_file_path):
    """
        驗證解壓縮後的影像是否與原始影像相同
    """
    original_image = cv2.imread(original_file_path)
    decompressed_image = cv2.imread(decompressed_file_path)
    
    if original_image is None:
        print(f"Error: 原始影像 {original_file_path} 讀取失敗")
        return False
    if decompressed_image is None:
        print(f"Error: 解壓縮後的影像 {decompressed_file_path} 讀取失敗")
        return False
    
    if np.array_equal(original_image, decompressed_image):
        print("解壓縮後的影像與原始影像相同")
        return True
    else:
        print("解壓縮後的影像與原始影像不相同")
        return False

def main():
    image_folder_path = "./image/"
    compress_folder_path = "./compressResult/"
    decompress_folder_path = "./decompressResult/"
    
    sum_ratio = 0

    for i in range(1, 4):
        image_path = f"{image_folder_path}img{i}.bmp"
        compressed_file_path = f"{compress_folder_path}img{i}.rle"
        decompressed_file_path = f"{decompress_folder_path}img{i}.bmp"
        
        print(f"=======處理影像: {image_path}=======")
        
        _, ratio = rle_compress_2d(image_path, compressed_file_path)
        sum_ratio += ratio
        
        _ = decompress_image_rle(compressed_file_path, decompressed_file_path)
        
        vertify_decompress(image_path, decompressed_file_path)
        
    average_ratio = sum_ratio / 3
    print(f"\n========平均壓縮率: {average_ratio}%=========")
        
if __name__ == "__main__":
    main()
            
        