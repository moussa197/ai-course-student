"""Configuration commune ; paramètres publics sans résultats futurs."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def load_config(path=None):
    """Charge la configuration JSON située dans le kit courant."""
    return json.loads(Path(path or ROOT / 'config.json').read_text(encoding='utf-8'))
