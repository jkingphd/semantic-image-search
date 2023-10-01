from pymilvus import connections, Collection
import streamlit as st
from PIL import Image
import numpy as np
import open_clip
import torch
import h5py
import os

@st.cache_data
def get_creds():
    creds = {}
    creds['host'] = os.environ['MILVUS_HOST']
    creds['port'] = os.environ['MILVUS_PORT']
    creds['user'] = os.environ['MILVUS_USER']
    creds['password'] = os.environ['MILVUS_PASS']
    return creds

creds = get_creds()
connections.connect(**creds)
collection = Collection('unsplash_lite')
collection.load()

@st.cache_resource
def load_model_and_preprocessor(target='hf-hub:laion/CLIP-ViT-B-16-laion2B-s34B-b88K'):
    if torch.cuda.is_available():
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')
    model, _, preprocess = open_clip.create_model_and_transforms(target)
    model.to(device)
    return model, preprocess, device
model, preprocess, device = load_model_and_preprocessor()

def get_text_vector(text, model=model, device=device):
    tokens = open_clip.tokenizer.tokenize([text])
    text_vector = model.encode_text(tokens.to(device))
    text_vector = text_vector.cpu().detach().numpy()
    text_vector /= np.linalg.norm(text_vector, axis=1, keepdims=True)
    return text_vector

def get_image_vector(image, model=model, device=device):
    image = preprocess(image)[None,:,:,:]
    image_vector = model.encode_image(image.to(device))
    image_vector = image_vector.cpu().detach().numpy()
    image_vector /= np.linalg.norm(image_vector, axis=1, keepdims=True)
    return image_vector

def get_top_k(query_vector, k=3, collection=collection):
    search_param = {
        "data": query_vector,
        "anns_field":"image",
        "param": {'metric_type': "COSINE", "params":{"nprobe": k}, "offset": 0},
        "limit": k,
        "output_fields": ['fname', 'photo_description']
    }
    results = collection.search(**search_param)
    y_dist = results[0].distances
    y_pred = [result.entity.get('fname') for result in results[0]]
    return y_dist, y_pred

st.title('Image Semantic Search')
y_dist = []
with st.form("text_form"):
    st.text_input("Search by description", "Superhero squad.", key="text")
    submitted = st.form_submit_button("Search")
    if submitted:
        query_vector = get_text_vector(st.session_state.text)
        y_dist, y_pred = get_top_k(query_vector, k=3)

with st.form("image_form"):
    uploaded_file = st.file_uploader("Search by image", type=['jpg', 'png'])
    submitted = st.form_submit_button("Search")
    if submitted:
        image = Image.open(uploaded_file)
        image.thumbnail((512,512))
        st.write('Uploaded image.')
        st.image(image)
        query_vector = get_image_vector(image)
        y_dist, y_pred = get_top_k(query_vector, k=3)

if len(y_dist) > 0:
    for dist, fname in zip(y_dist, y_pred):
        st.write(f'{fname} | Similarity: {dist:0.3f}')
        st.image(fname)
