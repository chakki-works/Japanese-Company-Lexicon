# LSTM params setting
class TrainingConfig(object):
    batch_size = 64 
    lr = 0.001 # learning rate
    epoches = 15
    print_step = 10


class LSTMConfig(object):
    emb_size = 128  # char vector embedding size
    hidden_size = 128  # lstm hidden layer dimensions
