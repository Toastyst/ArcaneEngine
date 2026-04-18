import shutil
import os

addon_src = 'ArcaneEngine'
addon_dst = r'D:\World of Warcraft\_retail_\Interface\AddOns\ArcaneEngine'

# Copy files, exclude .git
for root, dirs, files in os.walk(addon_src):
    if '.git' in dirs:
        dirs.remove('.git')
    for file in files:
        src_path = os.path.join(root, file)
        dst_path = os.path.join(addon_dst, os.path.relpath(src_path, addon_src))
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)

print("Addon synced to live.")