# Attentional Seq2seq model.
# Hyperparameters not specified here will take the default values.

num_units = 1000
embedding_dim = 500

embedder = {
    'dim': embedding_dim
}
encoder = {
    'rnn_cell_fw': {
        'kwargs': {
            'num_units': num_units
        }
    }
}
decoder = {
    'rnn_cell': {
        'kwargs': {
            'num_units': num_units
        },
    },
    'attention': {
        'kwargs': {
            'num_units': num_units,
        },
        'attention_layer_size': num_units
    }
}
