from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
import json
import pandas as pd
import time
import datetime
import random
from time import sleep
from bs4 import BeautifulSoup
from requests import get
from urllib.parse import unquote # to decode the url
import string
import unicodedata
import re

import pandas as pd
import numpy as np
import numpy as np
import numpy


from is_testing import OFFLINE_TESTING, REPORT_ENABLED


if not OFFLINE_TESTING and REPORT_ENABLED:
    from vllm import LLM, SamplingParams
    import torch
    import json

    model3 = LLM(
    #model = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
    model = "Valdemardi/DeepSeek-R1-Distill-Llama-70B-AWQ",
    #dtype=torch.bfloat16,
    #quantization="bitsandbytes", load_format="bitsandbytes",
    #max_model_len=8192,
    max_num_batched_tokens=4096,
    max_model_len=4096,
    enable_prefix_caching=False,
    gpu_memory_utilization=0.6,
    #quantization="w8a8",
    download_dir="./distilled_local",
    enforce_eager = True,
    )

    # model3 = LLM(
    #     model = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
    #     #model="/export/home/acs/stud/v/victor.boiangiu/dsm_project/distilled_local",
    #     dtype=torch.bfloat16, 
    #     quantization="bitsandbytes", load_format="bitsandbytes",
    #     #max_model_len=8192,
    #     max_model_len=4096,
    #     enable_prefix_caching=False,
    #     gpu_memory_utilization=0.6,
    #     #quantization="fp8",
    #     download_dir="./distilled_local",
    # )

if not OFFLINE_TESTING:
    from transformers import BertForSequenceClassification, TrainingArguments, Trainer, AutoModel, AutoTokenizer, AutoModel, get_constant_schedule, \
    get_constant_schedule_with_warmup, get_linear_schedule_with_warmup, pipeline, BertTokenizer, XLMRobertaForSequenceClassification
    from transformers.optimization import Adafactor, AdafactorSchedule
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from datasets import Dataset
    import torch
    from vllm import LLM, SamplingParams
    import torch
    import json

if not OFFLINE_TESTING:
    model = AutoModelForCausalLM.from_pretrained("./rollama_lora_merged_7b", load_in_8bit=True, device_map="auto")
    tokenizer = AutoTokenizer.from_pretrained("./rollama_lora_merged_7b")


    sampling_params = SamplingParams(
        temperature=0.6,
        top_p = 0.8,
        top_k = 20,
        min_p = 0,
        max_tokens=4096
    )

BASE_PROMPT = """You are a tool that turns news articles into realistic Google search queries someone might use to find the article. I have provided a few examples, please do the same for the last article.

<article>
Femeie de 26 de ani gasita moarta in apartamentul sau din Chicago luni.

Politia spune ca sotul ei este suspectul principal.
</article>

search query: femeie ucisa de sotul ei in chicago articol

<article>
Tesla dezvaluie noul camion electric joi, avand o autonomie de pana la 1000 de km...
</article>

search query: tesla nou camion electric 2025 autonomie

<article>
Kim Jong Un promite „sprijinul necondiționat” al Coreei de Nord pentru Rusia.

Liderul nord-coreean Kim Jong Un a promis Moscovei „sprijin necondiționat” cu privire la Ucraina
</article>

search query: Coreea de Nord sustine Rusia in razboiul cu Ucraina

<article>
{}
</article>

search query: """

def get_query(article):
    if OFFLINE_TESTING:
        return "Test query"

    input_text = BASE_PROMPT.format(article)
    input_ids = tokenizer(input_text, truncation=True, max_length=1024, return_tensors="pt").to(torch.device('cuda'))
    
    outputs = model.generate(**input_ids,
                             max_new_tokens=100
                            )
    decoded_output = tokenizer.decode(outputs[0])

    #print(decoded_output)
    
    return decoded_output.split("search query: ")[4].split("\n")[0].strip()

#get_query(TEST_INPUT_ARTICLE)

if not OFFLINE_TESTING:
    tokenizer2 = AutoTokenizer.from_pretrained("./final_xlm_roberta")
    model2 = XLMRobertaForSequenceClassification.from_pretrained("./final_xlm_roberta", num_labels=2).to('cuda')
    model2.eval()

def check_match(sample):
    if OFFLINE_TESTING:
        return True

    t1 = sample['title1'] + ". " + sample['text1']
    t2 = sample['title2'] + ". " + sample['text2']

    inputs = tokenizer2(
        t1,
        t2,
        return_tensors="pt",
        truncation=True,
        padding='max_length',
        max_length=512
    ).to('cuda')  # Send input to GPU
    
    # Generate prediction
    with torch.no_grad():
        outputs = model2(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()
    
    return predicted_class






BASE_PROMPT2 = """O să iți dau două articole, te rog să verifici dacă acestea coincid din punct de vedere al informațiilor prezentate și al tonului. Spune-mi dacă vreunul menționează lucruri pe care celălalt nu le menționează sau dacă acestea diferă in ton, unul fiind critic și celalalt de acord cu un eveniment, de exemplu. Scrie-mi un raport scurt cu cele detectate. Scrie-mi raportul în limba română.

<articol_1>
{}
</articol_1>
<articol_2>
{}
</articol_2>
<think>
"""

def get_report(article1, article2):
    if OFFLINE_TESTING or not REPORT_ENABLED:
        return "test report"

    prompt = BASE_PROMPT2.format(article1[:4500], article2[:4500])

    # Run batched inference
    result = model3.generate(prompt, sampling_params)
    
    response_text = result[0].outputs[0].text.strip()

    pos = response_text.find("</think>")

    if pos == -1:
        return response_text
    
    return response_text[pos + len("</think>") :].strip()
