# envault

> CLI tool to securely store and sync environment variables across machines using encrypted local storage

## Installation

```bash
pip install envault
```

## Usage

Initialize a vault in your project directory, then add and retrieve environment variables as needed.

```bash
# Initialize a new vault
envault init

# Add an environment variable
envault set API_KEY "your-secret-key"

# Retrieve a variable
envault get API_KEY

# List all stored variables
envault list

# Export variables to your shell environment
eval $(envault export)

# Sync vault to another machine
envault sync --remote user@host:/path/to/vault
```

Variables are encrypted at rest using AES-256 encryption. A master password is required on first use and cached securely in your system keychain.

## Requirements

- Python 3.8+
- `cryptography`
- `click`
- `keyring`

## License

MIT © [envault contributors](https://github.com/yourname/envault)