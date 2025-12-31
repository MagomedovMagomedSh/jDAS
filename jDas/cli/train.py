import hydra
from omegaconf import DictConfig
import mlflow
import pytorch_lightning as pl
from jdas.core.model import JDASUnet
from jdas.training.dataset import DASDataset

@hydra.main(version_base=None, config_path="../configs", config_name="train")
def train(cfg: DictConfig):
    """CLI команда для обучения"""
    
    # Настройка MLFlow
    mlflow.set_tracking_uri(cfg.logging.mlflow.tracking_uri)
    mlflow.set_experiment(cfg.logging.mlflow.experiment_name)
    
    with mlflow.start_run():
        # Логируем конфиг
        mlflow.log_params(dict(cfg))
        
        # Создаём модель и данные
        model = JDASUnet(learning_rate=cfg.model.learning_rate)
        dataset = DASDataset(cfg.data.path, cfg.data.channels)
        
        # Обучение
        trainer = pl.Trainer(
            max_epochs=cfg.training.epochs,
            accelerator="gpu" if cfg.training.gpus else "cpu"
        )
        
        trainer.fit(model, dataset)
        
        # Сохраняем модель
        torch.save(model.state_dict(), "jdаs_model.pth")
        mlflow.log_artifact("jdаs_model.pth")

if __name__ == "__main__":
    train()
