from __future__ import absolute_import

import numpy as np
import os
import shutil
import torch 
import time
import yaml

from easydict import EasyDict as edict

class AverageMeter(object):
    """Computes and stores the average and current value"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count if self.count != 0 else 0

def to_numpy(tensor):
    if torch.is_tensor(tensor):
        return tensor.cpu().numpy()
    elif type(tensor).__module__ != 'numpy':
        raise ValueError("Cannot convert {} to numpy array"
                         .format(type(tensor)))
    return tensor


def to_torch(ndarray):
    if type(ndarray).__module__ == 'numpy':
        return torch.from_numpy(ndarray).float()
    elif not torch.is_tensor(ndarray):
        raise ValueError("Cannot convert {} to torch tensor"
                         .format(type(ndarray)))
    return ndarray.float()

def get_config(fpath, type = 'train'):
    cfg = yaml.load(open(fpath))
    cfg = edict(cfg)

    tag = time.asctime(time.localtime(time.time()))
    tag = tag[4:-5] #remove day of the week and year
    cfg.TAG = tag
    if type == 'train':
        cfg.LOG.PATH = os.path.join(cfg.OUTPUT_DIR,cfg.TAG,'log.json')
        cfg.CHECKPOINT = os.path.join(cfg.OUTPUT_DIR,cfg.TAG)
        cfg.START_EPOCH = cfg.CURRENT_EPOCH #fresuming training
    if type == 'infer':
        cfg.CHECKPOINT = os.path.join(cfg.OUTPUT_DIR,cfg.TAG)
        cfg.IMG_RESULT = os.path.join(cfg.CHECKPOINT, 'img_result')
    return cfg

def save_config(cfg, fpath):
    cfg.RESUME_TRAINING = 1
    configpath = os.path.join(fpath, 'config.yml')
    yaml.dump(cfg, open(configpath,"w"))

def save_checkpoint(state, preds, cfg, log, is_best, fpath, filename='checkpoint.pth.tar', snapshot=None):
    preds = to_numpy(preds)
    latest_filepath = os.path.join(fpath, 'latest')

    if not os.path.exists(latest_filepath):
        os.makedirs(latest_filepath)

    log.save(latest_filepath)
    save_config(cfg, latest_filepath)
    torch.save(state, os.path.join(latest_filepath, filename))
    preds.dump(os.path.join(latest_filepath, 'preds.npy'))
    if snapshot and state['epoch'] % snapshot == 0:
        shutil.copytree(latest_filepath, os.path.join(fpath, str(state['epoch'])))

    if is_best:
        shutil.copytree(latest_filepath, os.path.join(fpath, "best"))

def save_preds(preds, checkpoint='checkpoint', filename='preds_valid.mat'):
    import scipy.io
    preds = to_numpy(preds)
    filepath = os.path.join(checkpoint, filename)
    scipy.io.savemat(filepath, mdict={'preds' : preds})
