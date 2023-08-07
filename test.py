#! /usr/bin/env python3

import onnx
import os
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import time
import tvm.relay as r
import tvm.ir as ir
from tvm.ir import IRModule
import tvm
from tvm.relay import testing
from tvm import autotvm
from tqdm import tqdm
from tvm.relay import qnn

import modman
import utils
import cgutils

# from support.data_loader import ImageNetDataset, CIFAR10Dataset

# from scipy.special import softmax
# import torch
# from torch.utils.data import DataLoader, TensorDataset
# from torchvision import transforms

batch_size = 5
image_size = 32
input_shape = (batch_size, 3, image_size, image_size)
# model_name = 'Q' + 'mobilenet_v2'
# dataset = 'CIFAR10'
# mode = 'none'

nchans = 123
data = r.var('data', shape=input_shape, dtype='uint8')
weight = r.var('weight', shape=(nchans, input_shape[1], 1, 1), dtype='int8')
x_zero_point = r.const(111, dtype='int32')
w_zero_point = r.const(222, dtype='int32')
x_scale = r.const(0.0078125, dtype='float32')
w_scale = r.const(0.0078125, dtype='float32')

qconv2d = qnn.op.conv2d(
            data,
            weight,
            x_zero_point,
            w_zero_point,
            x_scale,
            w_scale,
            kernel_size=[1, 1],
            channels=nchans,
            out_dtype='int32'
        )

mod = IRModule.from_expr(qconv2d)

# modman.build_module(mod, {}, export_path=None)

# input1 = r.var('input1', shape=(2,))
# input2 = r.var('input2', shape=(2,))
# e = r.add(input1, input2)
# mod = IRModule.from_expr(e)

mode = 'none'

mod, params = modman.get_irmod(
    # 'resnet50', 'CIFAR10', mode, 1, 32,
    # 'Qresnet50', 'CIFAR10', mode, 1, 32,
    # 'googlenet', 'CIFAR10', mode, 1, 32,
    'Qgooglenet', 'CIFAR10', mode, 1, 32,
    # 'densenet121', 'CIFAR10', mode, 1, 32,
    # 'Qdensenet121', 'CIFAR10', mode, 1, 32,
    # 'lenet5', 'MNIST', mode, 2, 32,
    # nchannels=1,
    allow_ep_load_failure=1,
)

mod = r.transform.InferType()(mod)
print(mod)
# modman.save_irmod_viz(mod, 'orig')

fn = mod['main']
const_args_extractor = cgutils.ConstArgsReplacer(fn.body)
fn_body, const_args = const_args_extractor.run()
fn = r.Function([x for x in fn.params] + list(const_args.keys()), fn_body, fn.ret_type, fn.type_params, fn.attrs)
mod = IRModule.from_expr(fn)
print(f'{const_args=}')
print(mod)

# mod, *_ = inst.instrument_module(
    # mod, mode, overall_cov=0, verbose=1, gn_last_n_layers=5
# )
with tvm.transform.PassContext(opt_level=3):
    mod, _ = r.optimize(mod, target=modman.targets['avx2'])
# mod = r.transform.FuseOps(fuse_opt_level=3)(mod)
print('-------------')
print(mod)

mod = r.transform.InferType()(mod)
# modman.save_irmod_viz(mod, 'inst')

# from tvm.contrib.target import onnx
# onnx.to_onnx(mod, {}, 'lenet5-inst', path='./lenet5-inst.onnx')

# with tvm.transform.PassContext(opt_level=0):
    # lib = r.build(mod, target=modman.targets['avx2'], params=params)

# lib = r.build(mod, target='llvm', params={
#     'input1': tvm.nd.array(np.array([1, 2], dtype='float32')),
#     'input2': tvm.nd.array(np.array([3], dtype='float32')),
# })

print('done')
