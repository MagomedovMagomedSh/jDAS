import mlflow
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
from omegaconf import DictConfig
import torch

from jdas.core.model import JDASUnet
from jdas.training.dataset import create_dataloaders

def train_model(cfg: DictConfig):
    """Основная функция обучения с MLFlow логированием"""
    
    # Настройка MLFlow
    mlflow.set_tracking_uri(cfg.logging.mlflow.tracking_uri)
    mlflow.set_experiment(cfg.logging.mlflow.experiment_name)
    
    with mlflow.start_run():
        # Логируем конфигурацию
        mlflow.log_params({
            "learning_rate": cfg.model.learning_rate,
            "batch_size": cfg.model.batch_size,
            "epochs": cfg.training.epochs,
            "channels": f"{cfg.data.channels[0]}-{cfg.data.channels[1]}"
        })
        
        # Создаём даталоадеры
        train_loader, val_loader = create_dataloaders(cfg)
        
        # Инициализируем модель
        model = JDASUnet(learning_rate=cfg.model.learning_rate)
        
        # Callbacks
        checkpoint_callback = ModelCheckpoint(
            dirpath="./checkpoints",
            filename="jdаs-{epoch:02d}-{val_loss:.2f}",
            save_top_k=1,
            monitor="val_loss",
            mode="min"
        )
        
        early_stopping = EarlyStopping(
            monitor="val_loss",
            patience=10,
            mode="min"
        )
        
        # Тренер
        trainer = pl.Trainer(
            max_epochs=cfg.training.epochs,
            accelerator="gpu" if torch.cuda.is_available() else "cpu",
            callbacks=[checkpoint_callback, early_stopping],
            log_every_n_steps=10,
            enable_progress_bar=True
        )
        
        # Обучение
        trainer.fit(model, train_loader, val_loader)
        
        # Сохраняем финальную модель
        model_path = get_model_path()
        model_path.parent.mkdir(exist_ok=True, parents=True)
        torch.save(model.state_dict(), model_path)
        mlflow.log_artifact(str(model_path))

        # Логируем метрики
        mlflow.log_metric("final_train_loss", trainer.callback_metrics.get("train_loss", 0))
        mlflow.log_metric("final_val_loss", trainer.callback_metrics.get("val_loss", 0))
        
        print(f"✅ Training complete! Model saved to {final_model_path}")
