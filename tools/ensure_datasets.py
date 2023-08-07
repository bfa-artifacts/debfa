#! /usr/bin/env python3

import sys
import os
sys.path.append(f'{os.path.dirname(os.path.realpath(__file__))}/..')

from torchvision import datasets
from tqdm import tqdm
import lpips

import cfg

def ensure_datasets(root=cfg.datasets_root):
    dataset_names = [
        'CIFAR10', 'CIFAR100', 'MNIST', 'FashionMNIST', 'DTD', 'GTSRB'
    ]
    for dataset_name in tqdm(dataset_names):
        train_kwargs = {
            'DTD': {'split': 'train'},
            'GTSRB': {'split': 'train'},
        }.get(dataset_name, {'train': True})

        test_kwargs = {
            'DTD': {'split': 'test'},
            'GTSRB': {'split': 'test'},
        }.get(dataset_name, {'train': False})

        datasets.__dict__[dataset_name](
            root=root, download=True, **train_kwargs
        )
        datasets.__dict__[dataset_name](
            root=root, download=True, **test_kwargs
        )
    lpips.LPIPS()

if __name__ == '__main__':
    ensure_datasets()
