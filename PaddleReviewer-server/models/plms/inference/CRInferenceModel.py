import os
import sys

import torch.nn as nn
import torch
import torch.nn.functional as F
from torch.nn import CrossEntropyLoss, BCEWithLogitsLoss
import numpy as np
from transformers import (
    RobertaConfig,
    RobertaModel,
    RobertaTokenizer,
    BartConfig,
    BartForConditionalGeneration,
    BartTokenizer,
    T5Config,
    T5ForConditionalGeneration,
    T5Tokenizer,
    AutoTokenizer,
)
import logging
from models.plms.code.models import ReviewerModel, load_model
import json




class CRModel():
    def __init__(self):
        mnt_dir="/data/DataLACP/rambo/data/codereviewer"
        model_path = os.path.join(mnt_dir, "codereviewer")
        max_source_length = 300
        max_target_length = 128
        mask_rate = 0.15 
        beam_size = 10
        device = torch.device("cpu")
        self.model_path = model_path
        self.max_source_length = max_source_length
        self.max_target_length = max_target_length
        self.mask_rate = mask_rate
        self.beam_size = beam_size
        self.device = device
        config_class, model_class, tokenizer_class = (T5Config, ReviewerModel, T5Tokenizer)
        config = config_class.from_pretrained(model_path)
        model = model_class.from_pretrained(model_path)
        config, model, tokenizer = load_model(
            config,
            model,
            tokenizer_class,
            add_lang_ids=True,
            tokenizer_path=model_path,
        )

        model_bin_path = os.path.join(model_path, "pytorch_model.bin")
        saved = model.cls_head
        model.cls_head = None
        model.load_state_dict(torch.load(model_bin_path, map_location="cpu"))
        model.cls_head = saved
        #model.to(args.local_rank)
        model.to(device)
        model.eval()
        self.model = model
        self.config = config
        self.tokenizer = tokenizer
        
    def predict(self, diff):
        difflines = diff.split("\n")[1:]        # remove start @@
        difflines = [line for line in difflines if len(line.strip()) > 0]
        map_dic = {"-": 0, "+": 1, " ": 2}
        def f(s):
            if s in map_dic:
                return map_dic[s]
            else:
                return 2
        labels = [f(line[0]) for line in difflines]
        difflines = [line[1:].strip() for line in difflines]
        inputstr = ""
        for label, line in zip(labels, difflines):
            if label == 1:
                inputstr += "<add>" + line
            elif label == 0:
                inputstr += "<del>" + line
            else:
                inputstr += "<keep>" + line
        source_ids = self.tokenizer.encode(inputstr, max_length=self.max_source_length, truncation=True)
        source_ids = source_ids[:self.max_source_length - 2]
        source_ids = [self.tokenizer.bos_id] + source_ids + [self.tokenizer.eos_id]
        pad_len = self.max_source_length - len(source_ids)
        source_ids += [self.tokenizer.pad_id] * pad_len

        input_labels = [-100] * len(source_ids)

        pred_ids, ex_ids = [], []
        source_ids = torch.tensor([source_ids], dtype=torch.long).to(self.device)
        source_mask = source_ids.ne(self.tokenizer.pad_id)
        preds = self.model.generate(source_ids,
                        attention_mask=source_mask,
                        use_cache=True,
                        num_beams=1,
                        max_length=self.max_target_length,
                        do_sample=False,
                        )
        top_preds = list(preds.cpu().numpy())
        pred_ids.extend(top_preds)
        pred_nls = [self.tokenizer.decode(id[1:], skip_special_tokens=True, clean_up_tokenization_spaces=False) for id in pred_ids]
        return pred_nls[0]
    
    def predict_quality(self, diff):
        difflines = diff.split("\n")[1:]
        difflines = [line for line in difflines if len(line.strip()) > 0] 
        input = " ".join(difflines)
        source_ids = self.tokenizer.encode(input, max_length=self.max_source_length, truncation=True)
        source_ids = torch.tensor([source_ids], dtype=torch.long).to(self.device)

        source_mask = source_ids.ne(self.tokenizer.pad_id)
        logits = self.model(
                cls=True,
                input_ids=source_ids,
                labels=None,
                attention_mask=source_mask
            )
        prediction = torch.argmax(logits, dim=-1).cpu().numpy()
        return int(prediction[0])
    
    def predict_review(self, diff):
        result = self.predict_quality(diff)
        if result == 0:
            return {"result": result, "review": "This code is good."}
        else:
            return {"result": result, "review": self.predict(diff)}

cr_model = CRModel()

if __name__ == "__main__":
    crmodel = CRModel()
    diff = "@@ -1,3 +1,3 @@\n-#include <iostream>\n+// #include <iostream>\n int main() {\n"
    print(crmodel.predict(diff))