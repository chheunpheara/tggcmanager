# Telegram Group and Channel Manager
This repository is served to manage Telegram groups and channels by connecting with the Telegram bot.

## Package Installation
```
pip install -r requirements
```

## Run the application
```
python MainApplication.py
```

## Packaging the application
```
pyinstaller -n <app_name> [options] -w MainApplication.py

#Update <app_name>.spec to include required folders
datas=[('contents', 'contents'), ('icons', 'icons')] # These two folders are currently important to be existed in the application packaging
```