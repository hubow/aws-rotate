# aws-rotate
Script to make the rotation of AWS Access and Secret Keys easier.
It generates new IAM keys and update local credentials file.

Passing account profile name, as an input parameter, is required.

## Usage
```
usage: aws-rotate.py [-h] [-p PROFILE]
```

## Example

```
⇒  ./aws-rotate.py -p playground
Backup file created - /Users/lukasz/.aws/credentials.bkp
[playground] New key created (*****CHDTX)
[playground] Old key was deleted from IAM (*****TJBOR)
```
