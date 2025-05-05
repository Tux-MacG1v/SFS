# SFS
A secure file storage system with end-to-end encryption, automatic expiration, and secure file sharing capabilities.


```markdown
# Secure File Storage (SFS) 🛡️

A secure file storage system with end-to-end encryption, automatic expiration, and secure file sharing capabilities.
![Secure Snonymous File Transfer](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDl0cHl1d3N5aGZndGd0cmQ5a2l0ZWp5YjZxN3BvZ2V4a3J0d3F3eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/du3J3cXyzhj8IOgv4q/giphy.gif)


## Features ✨

- **AES-256 Encryption** 🔒  
  Protect files with military-grade encryption during transfer and storage
- **Auto-Delete After Download** 🗑️  
  Files self-destruct after being downloaded (configurable)
- **Expiration Dates** ⏳  
  Set files to auto-delete after 1-30 days
- **Secure Sharing** 🔗  
  Generate protected download links with optional passwords
- **Parallel Uploads** ⚡  
  Upload multiple files simultaneously (10 concurrent threads)
- **Progress Tracking** 📊  
  Real-time upload speeds and ETA calculations
- **File Type Filtering** 📁  
  Whitelist specific file extensions (.txt, .pdf, .jpg, etc.)

## Installation ⚙️

### Requirements
- Python 3.9+
- pip package manager

```bash
# Clone repository
git clone https://github.com/Tux-MacG1v/SFS.git
cd secure-file-storage

# Install dependencies
pip install -r requirements.txt
```

## Configuration ⚙️

Create `config.json`:
```json
{
    "FOLDER_PATH": "uploads",
    "EXPIRE_DAYS": 15,
    "DELETE_AFTER": true,
    "SECRET_KEY": "YourStrongPassword123",
    "ENCRYPT": true,
    "API_URL": "https://files.tuxmacg1v.com/api/v1/upload",
    "MAX_RETRIES": 3,
    "MAX_WORKERS": 10,
    "SSL_VERIFY": true,
    "ALLOWED_EXTENSIONS": [".txt", ".pdf", ".docx", ".jpg", ".png"]
}
```

| Parameter           | Description                                | Default     |
|---------------------|--------------------------------------------|-------------|
| `FOLDER_PATH`       | Directory to monitor for files             | `uploads`   |
| `EXPIRE_DAYS`       | Days until file expiration                 | `15`        |
| `DELETE_AFTER`      | Auto-delete after download                 | `true`      |
| `SECRET_KEY`        | Encryption password (min 8 chars)          | **Required**|
| `ENCRYPT`           | Enable file encryption                     | `true`      |
| `API_URL`           | Upload endpoint URL                        | **Required**|
| `MAX_RETRIES`       | Max upload retry attempts                  | `3`         |
| `MAX_WORKERS`       | Concurrent upload threads                  | `10`        |
| `SSL_VERIFY`        | Enable SSL certificate verification        | `true`      |
| `ALLOWED_EXTENSIONS`| Permitted file types                       | **Required**|

## Usage 🚀

```bash
# Start the uploader
python uploader.py

# Sample output
2023-09-15 14:30:00,123 - INFO - Starting upload of 5 files (128.54 MB)
2023-09-15 14:30:15,456 - INFO - Uploaded secret_document.pdf (43.21 MB/s)
2023-09-15 14:30:20,789 - INFO - Generated link: https://files.tuxmacg1v.me/download/a1b2c3d4
```

Files will be:
1. Encrypted (if enabled)
2. Uploaded to secure storage
3. Deleted from local system (if configured)
4. Download links saved to `links.txt`

## API Documentation 📚

### Upload File
```http
POST /api/v1/upload
```
```json
{
    "file": "base64_encoded_data",
    "filename": "document.pdf",
    "encrypt": true,
    "secret_key": "YourPassword123",
    "expire_days": 15,
    "delete_after": true
}
```

### Download File
```http
GET https://files.tuxmacg1v.me/api/v1/download/{file_id}?key=YourPassword123
```

### File Management
```http
GET/DELETE https://files.tuxmacg1v.me/api/v1/files/{file_id}
```

## Troubleshooting 🚨

**Connection Issues**  
```bash
# Check API endpoint
curl -v https://files.example.com/api/v1/health

# Temporary disable SSL verification
Set "SSL_VERIFY": false in config.json
```

**Encryption Problems**  
```bash
# Verify secret key meets requirements
- Minimum 8 characters
- No special characters
- Matching on upload/download
```

## Contributing 🤝

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License 📄
MIT License - See [LICENSE](LICENSE) for details

---

**Disclaimer**: This project is intended for educational purposes. Use at your own risk.
``` 
