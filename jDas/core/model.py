import pytorch_lightning as pl
import torch
import torch.nn as nn


class JDASUnet(pl.LightningModule):
    """Упрощённая UNet для DAS очистки"""

    def __init__(self, learning_rate: float = 1e-3):
        super().__init__()
        self.save_hyperparameters()

        # Простая UNet архитектура
        self.encoder1 = nn.Sequential(
            nn.Conv1d(4, 32, 3, padding=1),
            nn.ReLU(),
            nn.Conv1d(32, 32, 3, padding=1),
            nn.ReLU(),
        )

        self.decoder1 = nn.Sequential(
            nn.ConvTranspose1d(32, 32, 3, padding=1),
            nn.ReLU(),
            nn.ConvTranspose1d(32, 4, 3, padding=1),
        )

        self.loss_fn = nn.MSELoss()

    def forward(self, x):
        if x.dim() == 4:
            x = x.squeeze(1)
        encoded = self.encoder1(x)
        return self.decoder1(encoded)

    def training_step(self, batch, batch_idx):
        noisy, clean = batch
        denoised = self(noisy)
        loss = self.loss_fn(denoised, clean)
        self.log("train_loss", loss)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.hparams.learning_rate)
