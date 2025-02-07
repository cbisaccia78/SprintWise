import json
import os
import sys

import numpy as np
import keras.api.layers as layers
import keras
import pdb

from sklearn.model_selection import train_test_split

# Load GloVe embeddings
MAX_TOKENS = 20000
MAX_LENGTH = 600
EMBEDDING_DIM = 300
NUM_HEADS = 4  # Number of attention heads
FF_DIM = 512  # Feedforward layer size
PATH_TO_GLOVE = os.getenv('GLOVE_PATH', None)

embeddings_index = {}
def parse_glove():
    with open(PATH_TO_GLOVE, 'r', encoding="utf-8") as f:
        for line in f:
            word, coefs = line.split(maxsplit=1)
            coefs = np.fromstring(coefs, 'f', sep=' ')
            embeddings_index[word] = coefs

parse_glove()

if len(sys.argv) != 2:
    print("Usage: python transformer_model.py json_data_path")
    sys.exit(1)

json_data_path = sys.argv[1]

# Load JSON data
with open(json_data_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Extract relevant data
titles, descriptions, code_snippets, labels = [], [], [], []

for entry in data:
    title = entry.get("title", "")
    description = entry.get("description", "")  # Placeholder for now
    original_files = entry.get("original_files", {})
    time_to_complete = entry.get("time_to_complete_hours", None)

    # Skip entries with missing labels
    if time_to_complete is None:
        continue

    # Concatenate all original file contents
    code = "\n".join(original_files.values()) if original_files else ""

    titles.append(title if title else "")
    descriptions.append(description if description else "")
    code_snippets.append(code if code else "")
    labels.append(time_to_complete)

# Convert lists to numpy arrays
title_text = np.array(titles, dtype=object)
description_text = np.array(descriptions, dtype=object)
code_text = np.array(code_snippets, dtype=object)
y_train = np.array(labels, dtype=np.float32)  # Target variable

print(y_train)

# Split data into train (70%), validation (15%), test (15%)
title_train, title_temp, desc_train, desc_temp, code_train, code_temp, y_train, y_temp = train_test_split(
    title_text, description_text, code_text, y_train, test_size=0.3, random_state=42)

title_val, title_test, desc_val, desc_test, code_val, code_test, y_val, y_test = train_test_split(
    title_temp, desc_temp, code_temp, y_temp, test_size=0.5, random_state=42)

# Function to create an embedding layer
def create_embedding_layer(text):
    text_vectorization = layers.TextVectorization(
        max_tokens=MAX_TOKENS,
        output_mode='int',
        output_sequence_length=MAX_LENGTH
    )
    try:
        text_vectorization.adapt(text)
    except ValueError:
        print('Error: No data found.')
        pdb.set_trace()

    vocabulary = text_vectorization.get_vocabulary()
    word_index = {word: i for i, word in enumerate(vocabulary)}

    embedding_matrix = np.zeros((MAX_TOKENS, EMBEDDING_DIM))
    for word, i in word_index.items():
        if i < MAX_TOKENS:
            embedding_vector = embeddings_index.get(word)
            if embedding_vector is not None and embedding_vector.shape == (EMBEDDING_DIM,):
                embedding_matrix[i] = embedding_vector
            else:
                embedding_matrix[i] = np.random.uniform(-0.05, 0.05, EMBEDDING_DIM) 

    embedding_layer = layers.Embedding(
        MAX_TOKENS,
        EMBEDDING_DIM,
        embeddings_initializer=keras.initializers.Constant(embedding_matrix),
        trainable=False,
        #mask_zero=True disable masking for now
    )

    return embedding_layer, text_vectorization

# Create embedding layers and vectorizers for each input
title_embedding_layer, title_vectorizer = create_embedding_layer(title_train)
description_embedding_layer, description_vectorizer = create_embedding_layer(desc_train)
code_embedding_layer, code_vectorizer = create_embedding_layer(code_train)

# Convert text inputs to integer sequences
title_train = title_vectorizer(title_train).numpy()
desc_train = description_vectorizer(desc_train).numpy()
code_train = code_vectorizer(code_train).numpy()

title_val = title_vectorizer(title_val).numpy()
desc_val = description_vectorizer(desc_val).numpy()
code_val = code_vectorizer(code_val).numpy()

title_test = title_vectorizer(title_test).numpy()
desc_test = description_vectorizer(desc_test).numpy()
code_test = code_vectorizer(code_test).numpy()

# Define model inputs
title_input = keras.Input(shape=(MAX_LENGTH,), dtype='int64')
desc_input = keras.Input(shape=(MAX_LENGTH,), dtype='int64')
code_input = keras.Input(shape=(MAX_LENGTH,), dtype='int64')

# Apply embedding layers (set trainable=True if desired)
title_features = title_embedding_layer(title_input)
desc_features = description_embedding_layer(desc_input)
code_features = code_embedding_layer(code_input)

# Add Position Embeddings
position_embedding = layers.Embedding(input_dim=MAX_LENGTH, output_dim=EMBEDDING_DIM)
title_pos = position_embedding(title_input)
desc_pos = position_embedding(desc_input)
code_pos = position_embedding(code_input)

title_features += title_pos
desc_features += desc_pos
code_features += code_pos


def transformer_encoder(inputs, head_size=256, num_heads=4, ff_dim=512, dropout=0.3):
    """Creates a Transformer Encoder Block."""
    # Multi-Head Self-Attention
    x = layers.MultiHeadAttention(num_heads=num_heads, key_dim=head_size)(inputs, inputs)
    x = layers.Dropout(dropout)(x)
    x = layers.LayerNormalization(epsilon=1e-6)(x)
    
    # Feed Forward Network
    x_ffn = layers.Dense(ff_dim, activation="relu")(x)
    x_ffn = layers.Dense(inputs.shape[-1])(x_ffn)
    
    # Add & Normalize
    x = layers.Add()([x, x_ffn])
    x = layers.LayerNormalization(epsilon=1e-6)(x)
    
    return x


# Transformer Blocks
title_features = transformer_encoder(title_features, head_size=EMBEDDING_DIM, num_heads=NUM_HEADS, ff_dim=FF_DIM)
desc_features = transformer_encoder(desc_features, head_size=EMBEDDING_DIM, num_heads=NUM_HEADS, ff_dim=FF_DIM)
code_features = transformer_encoder(code_features, head_size=EMBEDDING_DIM, num_heads=NUM_HEADS, ff_dim=FF_DIM)

# Pooling (Reduce Sequence to Fixed Size)
title_features = layers.GlobalAveragePooling1D()(title_features)
desc_features = layers.GlobalAveragePooling1D()(desc_features)
code_features = layers.GlobalAveragePooling1D()(code_features)

# Concatenate
x = layers.concatenate([title_features, desc_features, code_features])

# Dense layers
x = layers.Dense(256, activation='relu')(x)
x = layers.Dropout(0.3)(x)
x = layers.Dense(128, activation='relu')(x)
x = layers.Dropout(0.3)(x)

# Regression Output (time_to_complete_hours)
output = layers.Dense(1, activation='linear')(x)

# Create and compile model
model = keras.Model(
    inputs=[title_input, desc_input, code_input],
    outputs=output
)

model.compile(
    loss='mean_squared_error',
    optimizer='adam',
    metrics=['mean_absolute_error']
)

print(model.summary())


# Add early stopping and model checkpoint
early_stopping = keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=150,
    restore_best_weights=True
)

# Train the model
history = model.fit(
    [title_train, desc_train, code_train], y_train,
    validation_data=([title_val, desc_val, code_val], y_val),
    epochs=100000, batch_size=32,
    callbacks=[early_stopping]
)

# Evaluate on test set
test_loss, test_mae = model.evaluate([title_test, desc_test, code_test], y_test)
print(f"Test Loss: {test_loss:.4f}, Test MAE: {test_mae:.4f}")

# Save model
model.save("transformer_model.keras")