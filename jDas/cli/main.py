import subprocess
import sys
from pathlib import Path

import click
import uvicorn
from dotenv import load_dotenv

load_dotenv()


@click.group()
def cli():
    """DAS Cleaning Service CLI"""
    pass


@cli.command()
@click.option("--folder-url", required=True, help="Yandex Disk folder URL")
@click.option("--start", default=0, type=int, help="Start time (seconds)")
@click.option("--end", default=3600, type=int, help="End time (seconds)")
@click.option("--method", default="jdаs", type=click.Choice(["jdаs", "bandpass"]))
@click.option("--output-dir", default="./output", help="Output directory")
def process(folder_url: str, start: int, end: int, method: str, output_dir: str):
    """Process DAS data from Yandex Disk"""
    from jdas.api.processor import process_das_data

    result = process_das_data(
        folder_url=folder_url,
        time_range=(start, end),
        method=method,
        output_dir=Path(output_dir),
    )

    click.echo("✅ Processing complete!")
    click.echo(f"📁 Results saved to: {result['local_path']}")
    if result.get("yandex_url"):
        click.echo(f"☁️  Uploaded to Yandex Disk: {result['yandex_url']}")


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind")
@click.option("--port", default=8000, type=int, help="Port to bind")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def serve(host: str, port: int, reload: bool):
    """Start FastAPI web service"""
    from jdas.api.app import app

    uvicorn.run(app, host=host, port=port, reload=reload)


@cli.command()
def mlflow_ui():
    """Launch MLFlow UI for experiment tracking"""
    subprocess.run([sys.executable, "-m", "mlflow", "ui", "--port", "5000"])


@cli.command()
def dvc_pull():
    """Pull data from DVC remote"""
    subprocess.run(["dvc", "pull"])


@cli.command()
def dvc_push():
    """Push data to DVC remote"""
    subprocess.run(["dvc", "push"])


@cli.command()
@click.option("--token", help="Yandex OAuth token", envvar="YANDEX_DISK_TOKEN")
def setup_dvc(token: str):
    """Настроить DVC remote с Яндекс.Диском"""
    import os
    import subprocess

    if not token:
        token = os.getenv("YANDEX_DISK_TOKEN")
        if not token:
            click.echo("❌ Не найден YANDEX_DISK_TOKEN")
            click.echo("Добавьте в .env или укажите --token")
            return

    # Настраиваем DVC remote
    commands = [
        ["dvc", "remote", "add", "-d", "yandex", "disk://dvc-cache/"],
        ["dvc", "remote", "modify", "yandex", "type", "yandex"],
        ["dvc", "remote", "modify", "yandex", "token", token],
    ]

    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            click.echo(f"✅ {cmd}")
        else:
            click.echo(f"⚠️  {cmd}: {result.stderr}")

    click.echo("\n🎯 DVC настроен с Яндекс.Диском!")
    click.echo("Используйте: dvc push / dvc pull")


if __name__ == "__main__":
    cli()
