import json
import sys

import numpy as np
import tensorflow as tf
import tensorflow.keras.layers as layers
import tensorflow.keras as keras
from transformers import AutoTokenizer, TFAutoModel
from sklearn.model_selection import train_test_split

# Load CodeBERT tokenizer & model
MODEL_NAME = "microsoft/codebert-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
codebert = TFAutoModel.from_pretrained(MODEL_NAME)

# Function to tokenize inputs for CodeBERT
def tokenize_inputs(text_list, max_length=128):
    return tokenizer(
        text_list,
        padding=True,
        truncation=True,
        max_length=max_length,
        return_tensors="np"
    )

if len(sys.argv) != 2:
    print("Usage: python glove_lstm.py json_data_path")
    sys.exit(1)

json_data_path = sys.argv[1]

# Load JSON data
with open(json_data_path, "r", encoding="utf-8") as file:
    data = json.load(file)


# Extract data
titles, descriptions, code_snippets, labels = [], [], [], []

for entry in data:
    title = entry.get("title", "")
    description = entry.get("body", "")  # Issue description
    original_files = entry.get("original_files", {})
    time_to_complete = entry.get("time_to_complete_hours", None)

    if time_to_complete is None:
        continue  # Skip missing labels

    # Concatenate all original file contents
    code = "\n".join(original_files.values()) if original_files else ""

    titles.append(title)
    descriptions.append(description)
    code_snippets.append(code)
    labels.append(time_to_complete)

# Convert lists to NumPy arrays
y_data = np.array(labels, dtype=np.float32)

# Split into train (70%), validation (15%), test (15%)
title_train, title_temp, desc_train, desc_temp, code_train, code_temp, y_train, y_temp = train_test_split(
    titles, descriptions, code_snippets, y_data, test_size=0.3, random_state=42)

title_val, title_test, desc_val, desc_test, code_val, code_test, y_val, y_test = train_test_split(
    title_temp, desc_temp, code_temp, y_temp, test_size=0.5, random_state=42)

# Tokenize train, val, test datasets
title_train_enc = tokenize_inputs(title_train)
desc_train_enc = tokenize_inputs(desc_train)
code_train_enc = tokenize_inputs(code_train)

title_val_enc = tokenize_inputs(title_val)
desc_val_enc = tokenize_inputs(desc_val)
code_val_enc = tokenize_inputs(code_val)

title_test_enc = tokenize_inputs(title_test)
desc_test_enc = tokenize_inputs(desc_test)
code_test_enc = tokenize_inputs(code_test)

# Function to extract embeddings from CodeBERT
def extract_embeddings(inputs):
    """Extracts CodeBERT embeddings from tokenized inputs."""
    outputs = codebert(
        input_ids=tf.convert_to_tensor(inputs["input_ids"]),
        attention_mask=tf.convert_to_tensor(inputs["attention_mask"]),
        training=False
    )
    return outputs.last_hidden_state[:, 0, :]  # Use [CLS] token embedding

# Extract embeddings
title_train_emb = extract_embeddings(title_train_enc)
desc_train_emb = extract_embeddings(desc_train_enc)
code_train_emb = extract_embeddings(code_train_enc)

title_val_emb = extract_embeddings(title_val_enc)
desc_val_emb = extract_embeddings(desc_val_enc)
code_val_emb = extract_embeddings(code_val_enc)

title_test_emb = extract_embeddings(title_test_enc)
desc_test_emb = extract_embeddings(desc_test_enc)
code_test_emb = extract_embeddings(code_test_enc)

# Convert labels to tensors
y_train_tensor = tf.convert_to_tensor(y_train, dtype=tf.float32)
y_val_tensor = tf.convert_to_tensor(y_val, dtype=tf.float32)
y_test_tensor = tf.convert_to_tensor(y_test, dtype=tf.float32)

# Input layers
title_input = layers.Input(shape=(768,))
desc_input = layers.Input(shape=(768,))
code_input = layers.Input(shape=(768,))

# Concatenate features
x = layers.Concatenate()([title_input, desc_input, code_input])
x = layers.Dense(256, activation='relu')(x)
x = layers.Dropout(0.3)(x)
x = layers.Dense(128, activation='relu')(x)
x = layers.Dropout(0.3)(x)

# Regression output
output = layers.Dense(1, activation='linear')(x)

# Define Keras Model
model = tf.keras.Model(
    inputs=[title_input, desc_input, code_input],
    outputs=output
)

# Compile model
model.compile(
    loss='mean_squared_error',
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    metrics=['mean_absolute_error']
)

print(model.summary())

# Add early stopping and model checkpoint
early_stopping = keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=100,
    restore_best_weights=True
)

# Train model
history = model.fit(
    [title_train_emb, desc_train_emb, code_train_emb], y_train_tensor,
    validation_data=([title_val_emb, desc_val_emb, code_val_emb], y_val_tensor),
    epochs=10000, batch_size=4, callbacks=[early_stopping]
)

# Evaluate on test set
test_loss, test_mae = model.evaluate([title_test_emb, desc_test_emb, code_test_emb], y_test_tensor)
print(f"Test Loss: {test_loss:.4f}, Test MAE: {test_mae:.4f}")

# Save model
model.save("codebert_regression_model.keras")