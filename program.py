# Import necessary packages
import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display, Markdown
import PIL.Image
from dotenv import load_dotenv
import os
import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown
from transformers import BertForQuestionAnswering
from transformers import BertTokenizer
import torch
import numpy as np
import warnings
from transformers import logging

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, message="Some weights of the model checkpoint at")
logging.set_verbosity_error()


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
  raise ValueError("API key not found. Please set it in the .env file.")


genai.configure(api_key=api_key)

for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)
    
import PIL.Image

img = PIL.Image.open('people.jpg')
img

model = genai.GenerativeModel('gemini-pro-vision')

response = model.generate_content(img)

to_markdown(response.text)

response = model.generate_content(["Describe the image in detail including the color, products, and overall product description.", img], stream=True)
response.resolve()

to_markdown(response.text)

print(response.text)


model=BertForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")

tokenizer_for_bert=BertTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")

def bert_question_answer(question,passage,max_len=500):
  #Tokenize input question and passage
  #Include unique tokens- [CLS] and [SEP]
  input_ids = tokenizer_for_bert.encode (question, passage,  max_length= max_len, truncation=True)

  sep_index = input_ids.index(102)
  len_question = sep_index + 1
  len_passage = len(input_ids)- len_question

  #Need to separate question and passage
  #Segment ids will be 0 for question and 1 for passage
  segment_ids =  [0]*len_question + [1]*(len_passage)

  #Converting token ids to tokens
  tokens = tokenizer_for_bert.convert_ids_to_tokens(input_ids)


  #Getting start and end scores for answer
  #Converting input arrays to torch tensors before passing to the model
  start_token_scores = model(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]) )[0]
  end_token_scores = model(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]) )[1]


  #Converting scores tensors to numpy arrays
  start_token_scores = start_token_scores.detach().numpy().flatten()
  end_token_scores = end_token_scores.detach().numpy().flatten()

  #Getting start and end index of answer based on highest scores
  answer_start_index = np.argmax(start_token_scores)
  answer_end_index = np.argmax(end_token_scores)

  #Getting scores for start and end token of the answer
  start_token_score = np.round(start_token_scores[answer_start_index], 2)
  end_token_score = np.round(end_token_scores[answer_end_index], 2)

  #Combining subwords starting with ## and get full words in output.
  #It is because tokenizer breaks words which are not in its vocab.
  answer = tokens[answer_start_index]
  for i in range(answer_start_index + 1, answer_end_index + 1):
    if tokens[i][0:2] == '##':
      answer += tokens[i][2:]
    else:
      answer += ' ' + tokens[i]

  # If the answer didn't find in the passage
  if (start_token_score < 0 ) or ( answer_start_index == 0) or ( answer_end_index <  answer_start_index) or (answer == '[SEP]'):
    answer = "Sorry!, I was unable to discover an answer in the passage."

  return (answer_start_index, answer_end_index,  answer)

#Testing function
bert_question_answer("where is IIT kanpur situated", "Indian Institute of Technology Kanpur (IIT Kanpur) is a public institute of technology located in Kanpur, Uttar Pradesh, India. It was declared an Institute of National Importance by the Government of India under the Institutes of Technology Act. IIT Kanpur is ranked among the most prestigious academic institutions in India.[2]  The institution was established in 1959, as one of the first Indian Institutes of Technology, the institute was created with the assistance of a consortium of nine US research universities as part of the Kanpur Indo-American Programme (KIAP).[3][4]")


response_text_markdown = to_markdown(response.text)
print("Markdown Formatted Response Text:")
print(response_text_markdown)

# Example question
question = "What is the scenario of the picture?"

# Perform question answering
ans = bert_question_answer(question, response.text)

# Print the answer
print("Answer to the question:", ans)

