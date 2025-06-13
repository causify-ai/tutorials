import torch
import torch.nn as nn

class PositionalEncoding(nn.Module):
    def __init__(self, model_dim, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, model_dim)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, model_dim, 2).float() * (-torch.log(torch.tensor(10000.0)) / model_dim))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # shape: (1, max_len, model_dim)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:, :x.size(1)]
        return x

class SmallTransformer(nn.Module):
    def __init__(self, input_dim, model_dim=64, num_heads=4, num_layers=2, dropout=0.1):
        super().__init__()
        self.input_proj = nn.Linear(input_dim, model_dim)
        self.pos_encoder = PositionalEncoding(model_dim)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=model_dim,
            nhead=num_heads,
            dim_feedforward=128,
            dropout=dropout,
            batch_first=True  # [B, T, D]
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.output_layer = nn.Linear(model_dim, 1)

    def forward(self, x):  # x: [B, T, input_dim]
        x = self.input_proj(x)         # → [B, T, model_dim]
        x = self.pos_encoder(x)        # add positional info
        x = self.transformer_encoder(x)  # → [B, T, model_dim]
        x = x[:, -1, :]                # use the last time step
        return self.output_layer(x)   # → [B, 1]
    
class MultiStepTransformer(nn.Module):
    def __init__(self, input_dim=5, model_dim=64, num_heads=4, num_layers=2, dropout=0.1, forecast_horizon=30):
        super().__init__()
        self.embed = nn.Linear(input_dim, model_dim)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=model_dim,
            nhead=num_heads,
            dim_feedforward=128,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.output = nn.Linear(model_dim, forecast_horizon)  # predict 30 steps directly

    def forward(self, x):
        # x: [batch, 30, input_dim]
        x = self.embed(x)             # [batch, 30, model_dim]
        x = self.transformer(x)       # [batch, 30, model_dim]
        x = x[:, -1, :]               # use last time step's representation
        return self.output(x)         # [batch, 30]    