
from PIL import Image
import numpy as np
import tensorflow as tf
import cv2
import matplotlib.cm as cm
import io
import base64


def preprocess_image(image: Image.Image) -> np.ndarray:
    image = image.resize((224, 224))  
    image = np.array(image) 
    image = np.expand_dims(image, axis=0) 
    return image

def generate_gradcam(image_array, model, class_index, layer_name="top_conv"):
    grad_model = tf.keras.models.Model(
        inputs=[model.inputs],
        outputs=[model.get_layer(layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(image_array)
        loss = predictions[:, class_index]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs.numpy()[0]
    pooled_grads = pooled_grads.numpy()

    for i in range(pooled_grads.shape[-1]):
        conv_outputs[:, :, i] *= pooled_grads[i]

    heatmap = np.mean(conv_outputs, axis=-1)
    heatmap = np.maximum(heatmap, 0)
    heatmap /= np.max(heatmap)

    return heatmap

def overlay_heatmap(original_image, heatmap):
    heatmap = cv2.resize(heatmap, (original_image.size[0], original_image.size[1]))
    heatmap = np.uint8(255 * heatmap)
    heatmap = cm.jet(heatmap)[:, :, :3] 

    overlay = np.array(original_image) * 0.6 + heatmap * 0.4 * 255
    overlay = np.uint8(overlay)

    return Image.fromarray(overlay)

def encode_image_to_base64(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")