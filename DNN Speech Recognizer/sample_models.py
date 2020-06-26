from keras import backend as K
from keras.models import Model
from keras.layers import (BatchNormalization, Conv1D, Dense, Input, 
    TimeDistributed, Activation, Bidirectional, SimpleRNN, GRU, LSTM, MaxPooling1D, Dropout)

# using l2 regularization
from keras.regularizers import l2

def simple_rnn_model(input_dim, output_dim=29):
    """ Build a recurrent network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # Add recurrent layer
    simp_rnn = GRU(output_dim, return_sequences=True, 
                 implementation=2, name='rnn')(input_data)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(simp_rnn)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model

def rnn_model(input_dim, units, activation, output_dim=29):
    """ Build a recurrent network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # Add recurrent layer
    simp_rnn = GRU(units, activation=activation,
        return_sequences=True, implementation=2, name='rnn')(input_data)
    # TODO: Add batch normalization 
    bn_rnn = BatchNormalization(name='rnn_batch')(simp_rnn)
    # TODO: Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim, name='dense'))(bn_rnn)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model


def cnn_rnn_model(input_dim, filters, kernel_size, conv_stride,
    conv_border_mode, units, output_dim=29):
    """ Build a recurrent + convolutional network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # Add convolutional layer
    conv_1d = Conv1D(filters, kernel_size, 
                     strides=conv_stride, 
                     padding=conv_border_mode,
                     activation='relu',
                     name='conv1d')(input_data)
    # Add batch normalization
    bn_cnn = BatchNormalization(name='bn_conv_1d')(conv_1d)
    # Add a recurrent layer
    simp_rnn = SimpleRNN(units, activation='relu',
        return_sequences=True, implementation=2, name='rnn')(bn_cnn)
    # TODO: Add batch normalization
    bn_rnn = BatchNormalization(name='batch_normal')(simp_rnn)
    # TODO: Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim, name='dense_layer'))(bn_rnn)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: cnn_output_length(
        x, kernel_size, conv_border_mode, conv_stride)
    print(model.summary())
    return model

def cnn_output_length(input_length, filter_size, border_mode, stride,
                       dilation=1):
    """ Compute the length of the output sequence after 1D convolution along
        time. Note that this function is in line with the function used in
        Convolution1D class from Keras.
    Params:
        input_length (int): Length of the input sequence.
        filter_size (int): Width of the convolution kernel.
        border_mode (str): Only support `same` or `valid`.
        stride (int): Stride size used in 1D convolution.
        dilation (int)
    """
    if input_length is None:
        return None
    assert border_mode in {'same', 'valid'}
    dilated_filter_size = filter_size + (filter_size - 1) * (dilation - 1)
    if border_mode == 'same':
        output_length = input_length
    elif border_mode == 'valid':
        output_length = input_length - dilated_filter_size + 1
    return (output_length + stride - 1) // stride

def deep_rnn_model(input_dim, units, recur_layers, output_dim=29):
    """ Build a deep recurrent network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # TODO: Add recurrent layers, each with batch normalization
    #using bidrectional rnn with GRU
    input_rnn = Bidirectional(GRU(units, activation='relu',
        return_sequences=True, name='inpurt_gru'))(input_data)
    # apply batch normlization
    input_bn = BatchNormalization(name='input_bn')(input_rnn)
    # save last layer as reference
    # will go through a loop and add the new layers on it
    last_layer = input_bn
    for i in range(recur_layers):
        rnn_name = 'recure_rnn' + str(i)
        batch_name = 'recure_batch_normal' + str(i)
        
        rnn_layer = GRU(units, activation="relu",return_sequences=True, name=rnn_name)(last_layer)
        bn_layer = BatchNormalization(name=batch_name)(rnn_layer)
        last_layer = bn_layer
    
    # TODO: Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim, name='dense_layer'))(last_layer)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model

# This is my optional model
def deep_rnn_lstm_model(input_dim, units, recur_layers, output_dim=29):
    """ Build a deep recurrent network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # TODO: Add recurrent layers, each with batch normalization
    #using bidrectional rnn with GRU
    input_rnn = Bidirectional(LSTM(units, activation='relu',
        return_sequences=True, name='lstm_layer'))(input_data)
    # apply batch normlization
    input_bn = BatchNormalization(name='input_bn')(input_rnn)
    # save last layer as reference
    # will go through a loop and add the new layers on it
    last_layer = input_bn
    for i in range(recur_layers):
        rnn_name = 'recure_rnn' + str(i)
        batch_name = 'recure_batch_normal' + str(i)
        
        rnn_layer = LSTM(units, activation="relu",return_sequences=True, name=rnn_name)(last_layer)
        bn_layer = BatchNormalization(name=batch_name)(rnn_layer)
        last_layer = bn_layer
    
    # TODO: Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim, name='dense_layer'))(last_layer)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model

def bidirectional_rnn_model(input_dim, units, output_dim=29):
    """ Build a bidirectional recurrent network for speech
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # TODO: Add bidirectional recurrent layer
    bidir_rnn = Bidirectional(GRU(units, activation="relu", return_sequences=True, name='gru_input'))(input_data)
    # TODO: Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim, name='layer_desnse'))(bidir_rnn)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model

def final_model(input_dim, filters, kernel_size, stride,
    padding, units, recur_layers, output_dim=29, l2_lambda=0.001, dropout=0.2):
    """ Build a deep network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # TODO: Specify the layers in your network
#     input_rnn = Bidirectional(GRU(units, activation='relu',
#                             return_sequences=True, kernel_regularizer=l2(l2_lambda),
#                             recurrent_regularizer=l2(l2_lambda), name='input_gru_withl2'))(input_data)
    
#     # apply batch normalization
#     input_bn = BatchNormalization(name='batch_normal')(input_rnn)

    # Aconvolutional layer
    conv_1d = Conv1D(filters, kernel_size, 
                     strides=stride, 
                     padding=padding,
                     activation='relu',
                     name='conv1d')(input_data)
    # add max poling
    #pool = MaxPooling1D(strides=stride, name='pooling')(conv_1d)
    
    # Add batch normalization
    bn_cnn = BatchNormalization(name='bn_conv_1d')(conv_1d)


    last_layer = bn_cnn 
    
    for i in range(recur_layers):
        rnn_name = 'recure_rnn' + str(i)
        batch_name = 'recure_batch_normal' + str(i)
        
        rnn_layer = GRU(units, activation="relu",return_sequences=True, 
                 name=rnn_name, kernel_regularizer=l2(l2_lambda), dropout=dropout,
                 recurrent_regularizer=l2(l2_lambda))(last_layer)

        bn_layer = BatchNormalization(name=batch_name)(rnn_layer)
        last_layer = bn_layer
        
    # TODO: Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim, kernel_regularizer=l2(l2_lambda), name='dense_layer'))(last_layer)
    # TODO: Add softmax activation layer
    y_pred = Activation('softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    # TODO: Specify model.output_length
    model.output_length = lambda x: cnn_output_length(x, kernel_size, padding, stride)
    print(model.summary())
    return model