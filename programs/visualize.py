import matplotlib.pyplot as plt
import numpy as np

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


def pca_plot(input, labels, n_labels, save_path=None):

    pca = PCA(n_components=2).fit_transform(input)

    plt.figure(figsize=(5, 5))
    for i in range(n_labels):
        p = pca[labels==i]
        plt.scatter(p[:, 0], p[:, 1], label=str(i), alpha=0.5)
    plt.legend()
    plt.title('PCA')

    if save_path != None:
        plt.savefig(save_path)
    plt.show()


def tsne_plot(input, labels, n_labels, save_path=None):

    tsne= TSNE(n_components=2, random_state=0).fit_transform(input)

    plt.figure(figsize=(5, 5))
    for i in range(n_labels):
        p = tsne[labels==i]
        plt.scatter(p[:, 0], p[:, 1], label=str(i), alpha=0.5)
    plt.legend()
    plt.title('t-SNE')

    if save_path != None:
        plt.savefig(save_path)
    plt.show()

