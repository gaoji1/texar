#
"""
Base class for RNN decoders.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from tensorflow.contrib.seq2seq import Decoder as TFDecoder
from tensorflow.contrib.seq2seq import dynamic_decode

from txtgen.modules.module_base import ModuleBase
from txtgen.core.layers import get_rnn_cell, default_rnn_cell_hparams
from txtgen import context


class RNNDecoderBase(ModuleBase, TFDecoder):
    """Base class inherited by all RNN decoder classes.

    Args:
        cell (RNNCell, optional): If not specified, a cell is created as
            specified in :attr:`hparams["rnn_cell"]`.
        hparams (dict, optional): Hyperparameters. If not specified, the default
            hyperparameter setting is used. See :attr:`default_hparams` for the
            structure and default values.
        name (string): Name of the encoder.
    """

    def __init__(self, cell=None, hparams=None, name="rnn_decoder"):
        ModuleBase.__init__(name, hparams)
        self._helper = None
        self._initial_state = None
        if cell is not None:
            self._cell = cell
        else:
            self._cell = get_rnn_cell(self.hparams.rnn_cell)

    @staticmethod
    def default_hparams():
        """Returns a dictionary of hyperparameters with default values.

        The dictionary has the following structure and default values:

        .. code-block:: python

            {
                # A dictionary of rnn cell hyperparameters. See
                # `txtgen.core.layers.default_rnn_cell_hparams` for the
                # structure and default values. Ignored if :attr:`cell`
                # is given when constructing the decoder instance.
                "rnn_cell": default_rnn_cell_hparams,

                # `int32` scalar, maximum allowed number of decoding steps at
                # inference time.
                "max_decoding_length": 64
            }
        """
        return {
            "rnn_cell": default_rnn_cell_hparams(),
            "max_decoding_length": 64
        }


    def _build(self, helper, initial_state):    # pylint: disable=W0221
        """Performs decoding.

        Args:
            helper: An instance of `tf.contrib.seq2seq.Helper` that helps with
                the decoding process. For example, use an instance of
                `TrainingHelper` in training phase.
            initial_state: Initial state of decoding.

        Returns:
            `(outputs, final_state, sequence_lengths)`: `outputs` is an object
            containing the decoder output on all time steps, `final_state` is
            the cell state of the final time step, `sequence_lengths` is a
            Tensor of shape `[batch_size]`.
        """
        self._helper = helper
        self._initial_state = initial_state
        max_decoding_length = tf.cond(
            context.is_train(), None, self._hparams.max_decoding_length)

        outputs, final_state, sequence_lengths = dynamic_decode(
            decoder=self, maximum_iterations=max_decoding_length)

        self._add_internal_trainable_variables()
        # Add trainable variables of `self._cell` which may be constructed
        # externally
        self._add_trainable_variable(self._cell.trainable_variables())

        return outputs, final_state, sequence_lengths


    @property
    def batch_size(self):
        return self._helper.batch_size

    def initialize(self, name=None):
        """Called before any decoding iterations.

        This methods must compute initial input values and initial state.

        Args:
            name (string, optional): Name scope for any created operations.

        Returns:
            `(finished, initial_inputs, initial_state)`: initial values of
            'finished' flags, inputs and state.
        """
        raise NotImplementedError

    def step(self, time, inputs, state, name=None):
        """Called per step of decoding (but only once for dynamic decoding).

        Args:
            time: Scalar `int32` tensor. Current step number.
            inputs: RNNCell input (possibly nested tuple of) tensor[s] for this
                time step.
            state: RNNCell state (possibly nested tuple of) tensor[s] from
                previous time step.
            name: Name scope for any created operations.

        Returns:
            `(outputs, next_state, next_inputs, finished)`: `outputs` is an
            object containing the decoder output, `next_state` is a (structure
            of) state tensors and TensorArrays, `next_inputs` is the tensor that
            should be used as input for the next step, `finished` is a boolean
            tensor telling whether the sequence is complete, for each sequence
            in the batch.
        """
        raise NotImplementedError

    def finalize(self, outputs, final_state, sequence_lengths):
        raise NotImplementedError

