"""
Hydra entry point for training jDAS model
"""
import hydra
from omegaconf import DictConfig, OmegaConf


@hydra.main(version_base=None, config_path="../configs", config_name="train")
def main(cfg: DictConfig):
    """Main training function with Hydra"""
    from jdas.training.trainer import train_model

    print("🚀 Запуск обучения jDAS модели")
    print(f"Конфигурация:\n{OmegaConf.to_yaml(cfg)}")

    train_model(cfg)


if __name__ == "__main__":
    main()
