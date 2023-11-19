import os
# Specify the directory path
tfhub_cache_dir = '/tmp/tfhub_cache'

# Create the directory if it doesn't exist
if not os.path.exists(tfhub_cache_dir):
    os.makedirs(tfhub_cache_dir)
    
import streamlit as st
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import gridspec
import io
import cv2


os.environ['TFHUB_CACHE_DIR'] = '/tmp/tfhub_cache'  # You can change this path to any directory you prefer

# Load TF Hub module.
hub_handle = 'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2'
os.environ['TFHUB_CACHE_DIR'] = '/tmp/tfhub_cache'
hub_module = hub.load(hub_handle)

# Primary Image Processing Functions
def reduce_opacity(image, alpha):
  # Reduce the opacity of the input image by a factor of alpha
  return alpha * image + (1 - alpha) * tf.ones_like(image)

def brighten_image(image, factor):
  # Increase the brightness of the input image by a factor.
  return tf.clip_by_value(factor * image, 0.0, 1.0)

def upscale_image(image, scale_factor):
  # Upscale the input image with increased quality.
  target_size = tf.cast(tf.shape(image)[0:2] * scale_factor, tf.int32)
  return tf.image.resize(image, target_size, method=tf.image.ResizeMethod.BICUBIC)

def enhance_image(image):
    # Apply histogram equalization to enhance the contrast of the input image
    # Convert image to grayscale if it's RGB
    if image.shape[-1] == 3:
        image = tf.image.rgb_to_grayscale(image)
    
    # Convert TensorFlow tensor to NumPy array
    image_np = image.numpy()
    
    # Convert image to 8-bit integer
    image_np = (image_np * 255).astype(np.uint8)

    # Apply histogram equalization using OpenCV
    if len(image_np.shape) == 2:
        equalized_image_np = cv2.equalizeHist(image_np)
    else:
        equalized_image_np = cv2.equalizeHist(image_np[:, :, 0])

    # Convert back to float32 and TensorFlow tensor
    equalized_image = tf.convert_to_tensor(equalized_image_np, dtype=tf.float32) / 255.0

    return equalized_image


# def load_image(image, size):
#   # Load and convert to float32 numpy array, add batch dimension, and normalize to range [0, 1].
#   image = Image.open(image)
  
#   if image.mode != 'RGB':
#     image = image.convert('RGB')
#   image = np.array(image)
#   image = tf.image.convert_image_dtype(image, tf.float32)[tf.newaxis, ...]
  
#   return img
def fix_orientation(image):
    # Extract orientation from EXIF data
    exif = getattr(image, "_getexif", lambda: None)
    orientation = exif().get(274, 1) if exif else 1
    
    # Rotate image based on orientation
    if orientation == 3:
        image = image.rotate(180)
    elif orientation == 6:
        image = image.rotate(270)
    elif orientation == 8:
        image = image.rotate(90)

    return image

def load_image(file, image_size):
#   # Load and convert to float32 numpy array, add batch dimension, and normalize to range [0, 1].
#   img = tf.io.decode_image(image, channels=3, dtype=tf.float32)[tf.newaxis, ...]
    # Correct orientation using EXIF data
    
#   img = tf.image.resize(img, image_size, preserve_aspect_ratio=True)  
    # Read the content of the uploaded file
    image = Image.open(file)
    # image = fix_orientation(image)
    # Convert to a NumPy array
    # image = np.array(Image.open(io.BytesIO(content)))

    # Convert to RGB if the image has a different mode
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    image = np.array(image)
    # Convert to float32 and add batch dimension
    image = tf.image.convert_image_dtype(image, tf.float32)[tf.newaxis, ...]

    # Resize the image
    image = tf.image.resize(image, image_size, preserve_aspect_ratio=True)

    return image

def show_images(images, titles=('',)):
  image_sizes = [image.shape[1] for image in images]
  w = (image_sizes[0] * 6) // 320
  plt.figure(figsize=(w * len(images), w))
  gs = gridspec.GridSpec(1, len(images), width_ratios=image_sizes)
  
  for i in range(len(images)):
    plt.subplot(gs[i])
    plt.imshow(images[i][0], aspect='equal')
    plt.axis('off')
    plt.title(titles[i] if len(titles) > i else '')
  plt.show()
  
# Function to apply style transfer
def style_transfer(content_image, style_image):
    # Reduce opacity of style image
    alpha = 0.8
    style_image = reduce_opacity(style_image, alpha)

    # Brighten the style image
    brightness_factor = 1
    style_image = brighten_image(style_image, brightness_factor)

    # Enhance or upscale the style or content images if I want to
    # style_image = enhance_image(style_image)
    # style_image = upscale_image(style_image)
    
    outputs = hub_module(content_image, style_image)
    stylized_image = outputs[0]
    
    return stylized_image

# Streamlit app
def main():
    st.title("Image Style Transfer App")

    # Upload content and style images
    content_image = st.file_uploader("Upload Content Image", type=["jpg", "jpeg", "png"])
    style_image = st.file_uploader("Upload Style Image", type=["jpg", "jpeg", "png"])

    if content_image is not None and style_image is not None:
        # Preprocess images
        output_image_size = 400

        # Square output image
        content_img_size = (output_image_size, output_image_size)
        style_img_size = (256, 256) 

        content_image = load_image(content_image, content_img_size)
        style_image = load_image(style_image, style_img_size)
        style_image = tf.nn.avg_pool(style_image, ksize=[3,3], strides=[1,1], padding='SAME')

        # Reduce opacity of style image - slider input
        alpha = 0.8
        style_image = reduce_opacity(style_image, alpha)

        # Brighten the style image - slider input
        brightness_factor = 1
        style_image = brighten_image(style_image, brightness_factor)

        # Enhance the style image
        # style_image = enhance_image(style_image)
        stylized_image = style_transfer(content_image, style_image)
        
        # Convert tensorflow tensors to numpy array
        content_image_np = tf.squeeze(content_image).numpy()
        style_image_np = tf.squeeze(style_image).numpy()
        stylized_image_np = tf.squeeze(stylized_image).numpy()
        
        # Display images
        # Get aspect ratios of original images
        content_aspect_ratio = content_image_np.shape[0] / content_image_np.shape[1]
        style_aspect_ratio = style_image_np.shape[0] / style_image_np.shape[1]

        # Display images in columns with adjusted aspect ratios
        col1, col2 = st.columns(2)

        with col1:
            st.image(content_image_np, caption='Content Image', use_column_width=True)
        with col2:
            st.image(stylized_image_np, caption='Stylized Image', use_column_width=True)
            
        # st.image([content_image_np, style_image_np, stylized_image_np], caption = ['Content Image', 'Style Image', 'Stylized Image'], use_column_width=True)

# # Load and preprocess image function
# def load_image(image):
#     image = Image.open(image)
#     image = np.array(image)
#     image = tf.image.convert_image_dtype(image, tf.float32)[tf.newaxis, ...]
#     return image

if __name__ == "__main__":
    main()
