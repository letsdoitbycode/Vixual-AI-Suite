from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image
from transformers import BertForQuestionAnswering, BertTokenizer
import torch
import numpy as np
import io
import warnings
from transformers import logging

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, message="Some weights of the model checkpoint at")
logging.set_verbosity_error()

app = Flask(__name__)

# Model 1
model1 = genai.GenerativeModel('gemini-pro-vision')

# Model 2
model2 = BertForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
tokenizer2 = BertTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")

# Model 3
model3 = genai.GenerativeModel('gemini-pro-vision')
bert_model3 = BertForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
bert_tokenizer3 = BertTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/model1')
def model1_page():
    return render_template('model1.html')

@app.route('/model2')
def model2_page():
    return render_template('model2.html')

@app.route('/model3')
def model3_page():
    return render_template('model3.html')

@app.route('/generate_description', methods=['POST'])
def generate_description():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'})

    img_file = request.files['image']
    img_bytes = img_file.read()
    img = Image.open(io.BytesIO(img_bytes))

    response = model1.generate_content([
        "Describe the image in detail including overall description of the color, products, texture, lighting, scale, movement, emotion, and context.",
        img
    ], stream=True)
    response.resolve()
    description = response.text.strip().replace('\n', ' ')

    return jsonify({'description': description})

@app.route('/get_answer', methods=['POST'])
def get_answer():
    question = request.form['question']
    passage = request.form['passage']
    answer = bert_question_answer(question, passage)
    return jsonify(answer)

def bert_question_answer(question, passage, max_len=500):
    input_ids = tokenizer2.encode(question, passage, max_length=max_len, truncation=True)
    sep_index = input_ids.index(102)
    len_question = sep_index + 1
    len_passage = len(input_ids) - len_question
    segment_ids = [0] * len_question + [1] * len_passage

    start_token_scores = model2(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]))[0]
    end_token_scores = model2(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]))[1]

    start_token_scores = start_token_scores.detach().numpy().flatten()
    end_token_scores = end_token_scores.detach().numpy().flatten()

    answer_start_index = np.argmax(start_token_scores)
    answer_end_index = np.argmax(end_token_scores)

    start_token_score = np.round(start_token_scores[answer_start_index], 2)
    end_token_score = np.round(end_token_scores[answer_end_index], 2)

    tokens = tokenizer2.convert_ids_to_tokens(input_ids)
    answer = tokens[answer_start_index]
    for i in range(answer_start_index + 1, answer_end_index + 1):
        if tokens[i][0:2] == '##':
            answer += tokens[i][2:]
        else:
            answer += ' ' + tokens[i]

    if (start_token_score < 0) or (answer_start_index == 0) or (answer_end_index < answer_start_index) or (answer == '[SEP]'):
        answer = "Sorry!, I was unable to discover an answer in the passage."

    return answer

@app.route('/generate_and_answer', methods=['POST'])
def generate_and_answer():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'})

    img_file = request.files['image']
    img_bytes = img_file.read()
    img = Image.open(io.BytesIO(img_bytes))

    response = model3.generate_content([
        "Describe the image in detail including overall description of the color, products, texture, lighting, scale, movement, emotion, and context.",
        img
    ], stream=True)
    response.resolve()
    description = response.text.strip().replace('\n', ' ')

    question = request.form['question']
    answer = bert_question_answer_model3(question, description)

    return jsonify({'description': description, 'answer': answer})

def bert_question_answer_model3(question, passage, max_len=500):
    input_ids = bert_tokenizer3.encode(question, passage, max_length=max_len, truncation=True)
    sep_index = input_ids.index(102)
    len_question = sep_index + 1
    len_passage = len(input_ids) - len_question
    segment_ids = [0] * len_question + [1] * len_passage

    start_token_scores = bert_model3(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]))[0]
    end_token_scores = bert_model3(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]))[1]

    start_token_scores = start_token_scores.detach().numpy().flatten()
    end_token_scores = end_token_scores.detach().numpy().flatten()

    answer_start_index = np.argmax(start_token_scores)
    answer_end_index = np.argmax(end_token_scores)

    start_token_score = np.round(start_token_scores[answer_start_index], 2)
    end_token_score = np.round(end_token_scores[answer_end_index], 2)

    tokens = bert_tokenizer3.convert_ids_to_tokens(input_ids)
    answer = tokens[answer_start_index]
    for i in range(answer_start_index + 1, answer_end_index + 1):
        if tokens[i][0:2] == '##':
            answer += tokens[i][2:]
        else:
            answer += ' ' + tokens[i]

    if (start_token_score < 0) or (answer_start_index == 0) or (answer_end_index < answer_start_index) or (answer == '[SEP]'):
        answer = "Sorry!, I was unable to discover an answer in the passage."

    return answer

if __name__ == '__main__':
    app.run(debug=True)
