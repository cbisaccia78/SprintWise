import os

import keras
import keras.api.layers as layers
import numpy as np

MAX_TOKENS = 20000
MAX_LENGTH = 600

PATH_TO_GLOVE = os.getenv('GLOVE_PATH', None)
EMBEDDING_DIM = 300

embeddings_index = {}
def parse_glove():
    with open(PATH_TO_GLOVE, 'r') as f:
        for line in f:
            word, coefs = line.split(maxsplit=1)
            coefs = np.fromstring(coefs, 'f', sep=' ')
            embeddings_index[word] = coefs

parse_glove()
for key, value in list(embeddings_index.items())[:5]:
    print(key, value)


def create_embedding_layer(text):
    text_vectorization = layers.TextVectorization(
        max_tokens=MAX_TOKENS,
        output_mode='int',
        output_sequence_length=MAX_LENGTH
    )

    text_vectorization.adapt(text)

    vocabulary = text_vectorization.get_vocabulary()

    word_index = dict(zip(vocabulary, range(len(vocabulary))))

    embedding_matrix = np.zeros((MAX_TOKENS, EMBEDDING_DIM))
    for word, i in word_index.items():
        if i < MAX_TOKENS:
            embedding_vector = embeddings_index.get(word)
            if embedding_vector is not None:
                embedding_matrix[i] = embedding_vector
    embedding_layer = layers.Embedding(
        MAX_TOKENS,
        EMBEDDING_DIM,
        embedding_initializer=keras.initializers.Constant(embedding_matrix),
        trainable=False,
        mask_zero=True
    )

    return embedding_layer

title_text = np.array(['Go build the next google'], ['quit your dayjob'])
description_text = np.array(['The quick brown fox'], ["it's starting to get too tedious"])
code_text = np.array(['def foo():\n    return 42'], ['def bar():\n    return 24'])
            
title_embedding_layer = create_embedding_layer(title_text)
description_embedding_layer = create_embedding_layer(description_text)
code_embedding_layer = create_embedding_layer(code_text)

title_input = keras.Input(shape=(None,), dtype='int64')
description_input = keras.Input(shape=(None,), dtype='int64')
code_input = keras.Input(shape=(None,), dtype='int64')

title_features = title_embedding_layer(title_input)
description_features = description_embedding_layer(description_input)
code_features = code_embedding_layer(code_input)

title_features = layers.LSTM(128)(title_features)
description_features = layers.LSTM(128)(description_features)
code_features = layers.LSTM(128)(code_features)

x = layers.concatenate([title_features, description_features, code_features])

x = layers.Dense(128, activation='relu')(x)

output = layers.Dense(1, activation='linear')(x)

model = keras.Model(
    inputs=[title_input, description_input, code_input],
    outputs=output
)

model.compile(
    loss='mean_squared_error',
    optimizer='adam',
    metrics=['mean_absolute_error']
)

print(model.summary())
