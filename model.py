# -*- coding: utf-8 -*-
"""ML_lab4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ECvACYxWNozehipvBhNMLFtJrv2lI7Nm
"""

#!pip install kaggle
#files.upload()
!mkdir -p ~/.kaggle
!cp /content/kaggle.json ~/.kaggle/
!chmod 600 /root/.kaggle/kaggle.json
!kaggle competitions download -c trad-chinese-reading-comprehension-test-for-llms
!unzip trad-chinese-reading-comprehension-test-for-llms.zip

import pandas as pd

# 讀取Excel檔案
df = pd.read_excel('AI.xlsx')

train_id = []
train_articles = []
train_questions = []
train_options1 = []
train_options2 = []
train_options3 = []
train_options4 = []
train_answer = []

# 取出每一列的資料
for index, row in df.iterrows():
    id = row['ID']
    article = row['文章']
    question = row['問題']
    option1 = row['選項1']
    option2 = row['選項2']
    option3 = row['選項3']
    option4 = row['選項4']
    answer = row['正確答案']

    train_id.append(id)
    train_articles.append(article)
    train_questions.append(question)
    train_options1.append(option1)
    train_options2.append(option2)
    train_options3.append(option3)
    train_options4.append(option4)
    train_answer.append(answer)

print(len(train_articles))

import pandas as pd

# 讀取Excel檔案
df_test = pd.read_excel('AI1000.xlsx')

test_id = []
test_articles = []
test_questions = []
test_options1 = []
test_options2 = []
test_options3 = []
test_options4 = []

# 取出每一列的資料
for index, row in df_test.iterrows():
    # 取得文章、問題、選項1~4、正確答案
    id = row['題號']
    article = row['文章']
    question = row['問題']
    option1 = row['選項1']
    option2 = row['選項2']
    option3 = row['選項3']
    option4 = row['選項4']

    test_id.append(id)
    test_articles.append(article)
    test_questions.append(question)
    test_options1.append(option1)
    test_options2.append(option2)
    test_options3.append(option3)
    test_options4.append(option4)

print(len(test_articles))

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer

label_mapping = {"選項1": 1, "選項2": 2, "選項3": 3, "選項4": 4}

class CustomDataset(Dataset):
    def __init__(self, articles, questions, options1, options2, options3, options4, answers, tokenizer, max_length):
        self.articles = articles
        self.questions = questions
        self.options1 = options1
        self.options2 = options2
        self.options3 = options3
        self.options4 = options4
        self.answers = answers
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.articles)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            text=self.articles[idx] + ' ' + self.questions[idx],
            text_pair = None,
            add_special_tokens=True,
            max_length=self.max_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )

        encoding_list = [encoding[key].squeeze() for key in encoding.keys()]

        inputs = {
            'input_ids': encoding_list[0],
            'attention_mask': encoding_list[1],
            'token_type_ids': encoding_list[2],
            'labels': int(self.answers[idx])
        }

        return inputs


# 載入預訓練的 tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')

# 創建自定義資料集
train_dataset = CustomDataset(
    articles=train_articles,
    questions=train_questions,
    options1=train_options1,
    options2=train_options2,
    options3=train_options3,
    options4=train_options4,
    answers=train_answer,
    tokenizer=tokenizer,
    max_length=128  # 這裡的 max_length 可以根據你的資料集和模型的需求進行調整
)

# 使用 DataLoader 加載資料
batch_size = 32
train_data_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

for batch in train_data_loader:
    input_ids = batch['input_ids']
    attention_mask = batch['attention_mask']
    token_type_ids = batch['token_type_ids']
    labels = batch['labels']

    # 打印數據，這裡只是一個例子，具體結構取決於你的數據集和模型的輸入要求
    print("Input IDs:", input_ids)
    print("Attention Mask:", attention_mask)
    print("Token Type IDs:", token_type_ids)
    print("Labels:", labels)

    # 確保只打印第一個 batch
    break

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import BertTokenizer

label_mapping = {"選項1": 1, "選項2": 2, "選項3": 3, "選項4": 4}

class CustomTestDataset(Dataset):
    def __init__(self, articles, questions, options1, options2, options3, options4, tokenizer, max_length):
        self.articles = articles
        self.questions = questions
        self.options1 = options1
        self.options2 = options2
        self.options3 = options3
        self.options4 = options4
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.articles)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            text=self.articles[idx] + ' ' + self.questions[idx],
            text_pair= None,
            add_special_tokens=True,
            max_length=self.max_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )

        # 將encoding轉換為列表
        encoding_list = [encoding[key].squeeze() for key in encoding.keys()]

        inputs = {
            'input_ids': encoding_list[0],
            'attention_mask': encoding_list[1],
            'token_type_ids': encoding_list[2],
        }

        return inputs

# 創建自定義 test 資料集
test_dataset = CustomTestDataset(
    articles=test_articles,
    questions=test_questions,
    options1=test_options1,
    options2=test_options2,
    options3=test_options3,
    options4=test_options4,
    tokenizer=tokenizer,
    max_length=32  # 根據你的資料集和模型的需求進行調整
)

# 使用 DataLoader 加載 test 資料
test_batch_size = 32  # 調整 batch size
test_data_loader = DataLoader(test_dataset, batch_size=test_batch_size, shuffle=False)

for batch in test_data_loader:
    input_ids = batch['input_ids']
    attention_mask = batch['attention_mask']
    token_type_ids = batch['token_type_ids']

    # 打印數據，這裡只是一個例子，具體結構取決於你的數據集和模型的輸入要求
    print("Input IDs:", input_ids)
    print("Attention Mask:", attention_mask)
    print("Token Type IDs:", token_type_ids)

    # 確保只打印第一個 batch
    break

from transformers import BertForSequenceClassification, AdamW
import torch.nn as nn

# 步驟 1: 定義模型
model = BertForSequenceClassification.from_pretrained('bert-base-chinese', num_labels=5)

# 步驟 2: 定義優化器和損失函數
optimizer = AdamW(model.parameters(), lr=2e-5)
loss_fn = nn.CrossEntropyLoss()

# 步驟 3: Fine-tune 模型
epochs = 1  # 調整 epoch 次數
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

for epoch in range(epochs):
    model.train()
    for batch_idx, batch in enumerate(train_data_loader):
        # 釋放不必要的變數
        torch.cuda.empty_cache()

        inputs = {key: value.to(device) for key, value in batch.items()}

        outputs = model(**inputs)
        logits = outputs.logits

        labels = inputs['labels']
        max_indices = torch.argmax(logits, dim=1)
        print("labels!: ", labels)
        print("predict: ", max_indices)
        loss = loss_fn(logits, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # 釋放不必要的變數
        torch.cuda.empty_cache()

        print(f'Epoch {epoch + 1}/{epochs}, Batch {batch_idx + 1}/{len(train_data_loader)}, Loss: {loss.item()}')

model.eval()
predictions = []

with torch.no_grad():
    for test_batch in test_data_loader:
        test_inputs = {key: test.to(device) for key, test in test_batch.items()}
        test_outputs = model(**test_inputs)
        test_logits = test_outputs.logits
        probabilities = torch.nn.functional.softmax(test_logits, dim=1)
        predicted_labels = torch.argmax(probabilities, dim=1)
        predictions.extend(predicted_labels.cpu().numpy())

result_df = pd.DataFrame({'ID': test_id, 'Answer': predictions})

result_df.to_csv('predictions.csv', index=False)