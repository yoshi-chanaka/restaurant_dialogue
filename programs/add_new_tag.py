# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

import guidedlda
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from visualize import pca_plot, tsne_plot

if __name__ == "__main__":

    filepath = r"../data/restaurants.tsv"
    restaurants_info = pd.read_table(filepath, header=0)

    catches_processed = list(restaurants_info['catch_processed'].values)
    vectorizer = CountVectorizer(min_df=1)
    X = vectorizer.fit_transform(catches_processed).toarray()
    vocab = vectorizer.get_feature_names_out()
    word2id = dict((v, idx) for idx, v in enumerate(vocab))

    seed_topic_list = [
        ['和食', '寿司'],
        ['焼肉', 'ホルモン', '炭火'],
        ['ラーメン'],
        ['中華'],
        ['イタリアン', 'フレンチ'],
        ['洋食'],
        ['焼き鳥', '炭火'],
        ['ワイン'],
    ]

    # LDA
    n_topics = 8
    seed_topics = {}
    for idx, topics in enumerate(seed_topic_list):
        for word in topics:
            seed_topics[word2id[word]] = idx
    model = guidedlda.GuidedLDA(n_topics=n_topics, n_iter=3000, random_state=0, refresh=300)
    model.fit(X, seed_topics=seed_topics, seed_confidence=1.)
    doc_topic = model.transform(X)

    # LDA結果表示
    print('results of LDA')
    n_top_words = 100
    topic_word = model.topic_word_
    for i, topic_dist in enumerate(topic_word):
        topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words+1):-1]
        print('-' * 30 + '\nTopic {}: {}'.format(i, ' '.join(topic_words)))
    print('=' * 30)

    # kmeansクラスタリング
    n_clusters = 5
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(doc_topic)
    for i in range(n_clusters):
        print('ratio of cluster {}: {:.4f}'.format(
            i + 1, (kmeans.labels_ == i).sum() / len(kmeans.labels_)
        ))

    # kmeans結果表示
    for label in range(n_clusters):
        idx = np.where(kmeans.labels_ == label)[0]
        for i in idx[:20]:
            print('Cluster {} | {}'.format(kmeans.labels_[i], catches_processed[i]))
        print('')

    # クラスタリングの結果をもとに，ラベルを入力
    another_labels = [input('label of cluster {}: '.format(i)) for i in range(n_clusters)]
    new_genres = [another_labels[c] for c in kmeans.labels_]

    save_path = '../data/restaurants_lda.tsv'
    f = open(save_path, 'w')
    f.write('name\tgenre\tnew_genre\tcatch\tcatch_processed\tplace\turl\n')

    for info_list, new_genre in zip(restaurants_info.values, new_genres):

        info_list = list(info_list)
        info_list.insert(2, new_genre)
        f.write('\t'.join(info_list) + '\n')

    f.close()

    # 可視化
    # PCA
    pca_plot(
        input=doc_topic,
        labels=kmeans.labels_,
        n_labels=n_clusters,
        save_path='../figures/pca.jpg'
    )

    # T-SNE
    tsne_plot(
        input=doc_topic,
        labels=kmeans.labels_,
        n_labels=n_clusters,
        save_path='../figures/tsne.jpg'
    )
