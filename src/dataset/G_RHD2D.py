# ------------------------------------------------------------------------------
# Copyright (c) Microsoft
# Licensed under the MIT License.
# Written by Bin Xiao (Bin.Xiao@microsoft.com)
# ------------------------------------------------------------------------------

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import copy
import logging
import random

import os
import cv2
import json
import pickle
import torch
import numpy as np
from easydict import EasyDict as edict

from src.dataset.BaseDataset import JointsDataset
from src.utils.imutils import im_to_torch, draw_heatmap
from src.utils.misc import to_torch
from src.utils.imutils import load_image
from src.core.evaluate import get_preds_from_heatmap

from .RHD2D import RHD2D
from .G2D import G2D
class G_RHD2D(JointsDataset):
    def __init__(self, cfg):
        super(G_RHD2D, self).__init__(cfg)
        self.rhd = RHD2D(cfg.RHD)
        self.G = G2D(cfg.G)

    def __len__(self):
        return len(self.rhd) + len(self.G)

    def _get_db(self):
        pass

    def __getitem__(self, idx):
        if idx < len(self.rhd):
            return self.rhd[idx]
        idx -= len(self.rhd)
        return self.G[idx]

    def eval_result(self, outputs, batch, cfg = None):
        preds = get_preds_from_heatmap(outputs['heatmap'][-1])
        # print (preds[0,:5,:], batch['coor'][0,:5,:])
        diff = batch['coor'] - preds
        dis = torch.norm(diff, dim = -1)
        PcK_Acc = (dis < self.cfg.THR).float().mean()
        return {"dis": dis.mean(), "PcKAcc":PcK_Acc}


    def get_preds(self, outputs):
        return get_preds_from_heatmap(outputs['heatmap'][-1])