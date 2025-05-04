import os
import json
import base64
import asyncio
import aiohttp
import logging
import time
import ssl
from tqdm import tqdm
from pathlib import Path
from datetime import timedelta
from typing import List, Dict

COLORS = {
    "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
    "cyan": "\033[96m", "magenta": "\033[95m", "reset": "\033[0m",
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('uploader.log'), logging.StreamHandler()]
)

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{COLORS['cyan']}{size_bytes:.2f} {unit}{COLORS['reset']}"
        size_bytes /= 1024
    return f"{COLORS['cyan']}{size_bytes:.2f} TB{COLORS['reset']}"

class AsyncUploader:
    def __init__(self, config_path: str = 'config.json'):
        self.config = self.load_config(config_path)
        self.validate_config()
        self.session = None
        self.total_files = 0
        self.success_count = 0
        self.failure_count = 0
        self.lock = asyncio.Lock()
        self.start_time = time.time()
        self.total_size = 0
        self.uploaded_size = 0

    def load_config(self, config_path: str) -> Dict:
        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Config error: {str(e)}")
            raise

    def validate_config(self):
        required_keys = ['FOLDER_PATH', 'EXPIRE_DAYS', 'DELETE_AFTER',
                        'SECRET_KEY', 'ENCRYPT', 'API_URL']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing config key: {key}")

    async def init_session(self):
        """Windows-safe session initialization"""
        ssl_context = ssl.create_default_context()
        if not self.config.get('SSL_VERIFY', True):
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        # Use system resolver instead of AsyncResolver
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                ssl=ssl_context,
                limit_per_host=self.config['MAX_WORKERS']
            ),
            timeout=aiohttp.ClientTimeout(total=300)
        )

    async def close_session(self):
        if self.session:
            await self.session.close()

    def get_files(self) -> List[str]:
        folder = Path(self.config['FOLDER_PATH'])
        if not folder.exists():
            raise FileNotFoundError(f"Folder {self.config['FOLDER_PATH']} not found")

        files = [str(f) for f in folder.glob('*') 
                if f.is_file() and f.suffix.lower() in self.config['ALLOWED_EXTENSIONS']]
        
        self.total_size = sum(os.path.getsize(f) for f in files)
        return files

    async def upload_file(self, file_path: str, semaphore: asyncio.Semaphore, main_bar: tqdm) -> bool:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        retries = 0
        
        with tqdm(total=file_size, desc=f"{COLORS['green']}{file_name[:20]:<20}{COLORS['reset']}", 
                 unit='B', unit_scale=True, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
                 leave=False) as file_bar:
            
            while retries <= self.config['MAX_RETRIES']:
                try:
                    with open(file_path, 'rb') as f:
                        content = base64.b64encode(f.read()).decode('utf-8')

                    payload = {
                        "file": content,
                        "filename": file_name,
                        "encrypt": self.config['ENCRYPT'],
                        "secret_key": self.config['SECRET_KEY'],
                        "expire_days": self.config['EXPIRE_DAYS'],
                        "delete_after": self.config['DELETE_AFTER']
                    }

                    async with semaphore, self.session.post(self.config['API_URL'], json=payload) as response:
                        if response.status == 201:
                            data = await response.json()
                            async with self.lock:
                                with open('links.txt', 'a') as f:
                                    f.write(f"{data['download_url']}\n")
                                if self.config['DELETE_AFTER']:
                                    os.remove(file_path)
                            
                            file_bar.update(file_size)
                            self.success_count += 1
                            return True
                        else:
                            raise Exception(f"API Error: {await response.text()}")
                            
                except Exception as e:
                    if retries == self.config['MAX_RETRIES']:
                        self.failure_count += 1
                        file_bar.colour = 'red'
                        file_bar.set_description(f"{COLORS['red']}{file_name[:20]:<20}{COLORS['reset']}")
                        file_bar.set_postfix_str(f"{COLORS['red']}Failed{COLORS['reset']}")
                        return False
                    retries += 1
                    file_bar.set_postfix_str(f"{COLORS['yellow']}Retry {retries}/{self.config['MAX_RETRIES']}{COLORS['reset']}")
                    await asyncio.sleep(2 ** retries)

    async def run(self):
        files = self.get_files()
        self.total_files = len(files)
        
        if not files:
            logging.info("No files found to upload")
            return

        logging.info(f"Starting upload of {self.total_files} files ({format_size(self.total_size)})")
        
        await self.init_session()
        semaphore = asyncio.Semaphore(self.config['MAX_WORKERS'])
        
        try:
            with tqdm(total=self.total_size, desc=f"{COLORS['magenta']}Overall Progress{COLORS['reset']}", 
                     unit='B', unit_scale=True, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as main_bar:
                
                tasks = [self.upload_file(f, semaphore, main_bar) for f in files]
                await asyncio.gather(*tasks)
                
            total_time = time.time() - self.start_time
            avg_speed = self.total_size / total_time if total_time > 0 else 0
            logging.info(
                f"\n{COLORS['green']}Upload complete!{COLORS['reset']}\n"
                f"Success: {COLORS['green']}{self.success_count}/{self.total_files}{COLORS['reset']}\n"
                f"Failed: {COLORS['red']}{self.failure_count}/{self.total_files}{COLORS['reset']}\n"
                f"Average Speed: {format_size(avg_speed)}/s\n"
                f"Total Time: {timedelta(seconds=int(total_time))}"
            )
        finally:
            await self.close_session()

if __name__ == "__main__":
    try:
        uploader = AsyncUploader()
        asyncio.run(uploader.run())
    except Exception as e:
        logging.error(f"{COLORS['red']}Critical error: {str(e)}{COLORS['reset']}")
        exit(1)