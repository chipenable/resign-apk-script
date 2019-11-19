# Re-sign apk script

Python script to re-sign apk files using repository with keystores. It can be useful for reverse-engineering purposes. 

### How to re-sign apk

Run python script with two parameters - keystore name and apk file path. 

```
./resign.py debug demo_app.apk
```

### How to add keys

Copy a new keystore to keystores directory. Describe this keystore in keystores.json file.