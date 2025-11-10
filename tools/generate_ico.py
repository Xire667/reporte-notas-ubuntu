"""Genera un .ico multiresolución a partir del PNG del logo.

- Origen: app/static/main/assets/img/logo-dsi.png
- Destino: app/static/main/assets/img/logo-dsi.ico

Incluye tamaños comunes para que Windows muestre el icono correcto
en distintos niveles de zoom del Explorador: 16, 24, 32, 48, 64, 128, 256.
"""

from PIL import Image
import os


def main():
    project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    png_path = os.path.join(project_root, 'app', 'static', 'main', 'assets', 'img', 'logo-dsi.png')
    ico_path = os.path.join(project_root, 'app', 'static', 'main', 'assets', 'img', 'logo-dsi.ico')

    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

    if not os.path.isfile(png_path):
        raise FileNotFoundError(f'No se encontró el PNG del logo en: {png_path}')

    img = Image.open(png_path).convert('RGBA')
    # Pillow puede generar el .ico con múltiples tamaños automáticamente
    img.save(ico_path, format='ICO', sizes=sizes)
    print(f'Icono multiresolución generado: {ico_path}')


if __name__ == '__main__':
    main()