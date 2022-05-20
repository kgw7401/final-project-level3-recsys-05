import os
import pickle
import numpy as np
from scipy.stats import beta
from sklearn.metrics.pairwise import cosine_similarity

from .model_architecture import SASRec, EASE

import torch

MODEL_PATH = '/opt/ml/final-project-level3-recsys-05/Model/Model-Experiment/model'

# item2vec
with open(os.path.join(MODEL_PATH, 'Word2Vec-CBOW-problem_association_seq-problem_level_seq-problem_tag_seq-vs128-vector.pickle'), 'rb') as file: 
    load_item2vec = pickle.load(file)

## Transformer
device = 'cuda' if torch.cuda.is_available() else 'cpu'

num_assessmentItemID = 23090
hidden_units = 128
num_heads = 8
num_layers = 1
dropout_rate = 0.5
num_workers = 8

# user_seq
user_seq = SASRec(
        num_assessmentItemID = num_assessmentItemID,
        hidden_units = hidden_units,
        num_heads = num_heads,
        num_layers = num_layers,
        dropout_rate = dropout_rate
        ).to(device)

# User-Seq-Transformer
# new-User-Seq-Transformer
user_seq.load_state_dict(torch.load(os.path.join(MODEL_PATH, 'new-User-Seq-Transformer' + '.pt')))

# pretrained_user_seq
pretrained_user_seq = SASRec(
        num_assessmentItemID = num_assessmentItemID,
        hidden_units = hidden_units,
        num_heads = num_heads,
        num_layers = num_layers,
        dropout_rate = dropout_rate
        ).to(device)

# User-Seq-Transformer
# new-Item2Vec-pretrained-User-Seq-Transformer
pretrained_user_seq.load_state_dict(torch.load(os.path.join(MODEL_PATH, 'new-Item2Vec-pretrained-User-Seq-Transformer' + '.pt')))

# ease
class MyCoustomUnpickler(pickle.Unpickler):
    def find_class(self, __module_name: str, __global_name: str):
        if __module_name == '__main__':
            __module_name = __name__
        return super().find_class(__module_name, __global_name)

with open(os.path.join(MODEL_PATH, 'ease.pickle'), 'rb') as file:
    ease = MyCoustomUnpickler(file)
    ease = ease.load()
    ease.device = device

def thompson_sampling(model_type_click_dict):
    '''
    
    model_type_click_dict = {
            'item2vec' : {'pos_click' : 1, 'total_view' : 1},
            'user_seq' : {'pos_click' : 1, 'total_view' : 1},
            'pretrained_user_seq' : {'pos_click' : 1, 'total_view' : 1},
    }

    '''

    A_sampling = beta.rvs(model_type_click_dict['item2vec']['pos_click'], model_type_click_dict['item2vec']['total_view'])
    
    B_sampling = beta.rvs(model_type_click_dict['user_seq']['pos_click'], model_type_click_dict['user_seq']['total_view'])
    
    C_sampling = beta.rvs(model_type_click_dict['pretrained_user_seq']['pos_click'], model_type_click_dict['pretrained_user_seq']['total_view'])
    
    # 가장 값이 높은 추천을 선택
    idx = np.argmax([A_sampling, B_sampling, C_sampling])
    
    if idx == 0: return 'item2vec'
    elif idx == 1: return 'user_seq'
    elif idx == 2: return 'pretrained_user_seq'

def ease_model(problem_seq):
    mat = torch.zeros(size = (1, num_assessmentItemID))
    mat[0, problem_seq] = 1
    output = ease.predict(mat)[0].cpu().numpy()
    ease.clear_memory()
    return output

def item2vec_model(problem_seq):
    cos_arr = cosine_similarity(load_item2vec[problem_seq[0]].reshape(1, -1), load_item2vec)[0]
    return cos_arr

def user_seq_model(problem_seq):
    user_seq.eval()
    input = {'assessmentItem' : torch.tensor([problem_seq[::-1]]) + 1}
    with torch.no_grad():
        output = user_seq(input)[0].cpu().numpy()
    return output

def pretrained_user_seq_model(problem_seq):
    pretrained_user_seq.eval()
    input = {'assessmentItem' : torch.tensor([problem_seq[::-1]]) + 1}
    with torch.no_grad():
        output = pretrained_user_seq(input)[0].cpu().numpy()
    return output
