import torch.nn as nn
import torch.nn.functional as F

class DQN(nn.Module):

    def __init__(self, in_channels):
        """
        Initialize a deep Q-learning network as described in
        https://storage.googleapis.com/deepmind-data/assets/papers/DeepMindNature14236Paper.pdf
        Arguments:
            in_channels: number of channel of input.
                i.e The number of most recent frames stacked together as describe in the paper
            num_actions: number of action-value to output, one-to-one correspondence to action in game.
        """
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(in_channels, 10)
        self.fc2 = nn.Linear(10, 10)
        self.fc3 = nn.Linear(10, 1)


    def forward(self, x):
        x = F.sigmoid(self.conv1(self.fc1))
        x = F.sigmoid(self.conv1(self.fc2))
        x = F.sigmoid(self.conv1(self.fc3))
        return x

    