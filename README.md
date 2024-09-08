
# dpsctl-gui.py

`dpsctl-gui.py` is a crude frontend for OpenDPS dpsctl

![dpsctl-gui in action](https://github.com/gabtremblay/dpsctl-gui/blob/main/assets/sc.png?raw=true)

## Requirements

The tool runs inside a Python virtual environment and requires the installation of certain Python dependencies listed in `requirements.txt`.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/gabtremblay/dpsctl-gui.git
```

### 2. Set up a Virtual Environment

Create a Python virtual environment:

```bash
python -m venv dpsctl-gui
```

Activate the virtual environment:

- On Linux/macOS:

  ```bash
  cd dpsctl-gui
  source bin/activate
  ```

- On Windows:

  ```bash
  cd dpsctl-gui
  Scripts\activate.ps1
  ```

### 3. Install Dependencies

Once the virtual environment is activated, install the necessary dependencies using the following command:

```bash
pip install -r requirements.txt
```

## Usage

To run the tool, you need to specify the `-d` parameter. This parameter can either be an IP address or a TTY device.

### Example usage:

```bash
python dpsctl-gui.py -d <device_ip_or_tty>
```

#### Examples:

- Using an IP address:

  ```bash
  python dpsctl-gui.py -d 192.168.1.10
  ```

- Using a TTY device:

  ```bash
  python dpsctl-gui.py -d /dev/ttyUSB0
  ```

If the `-d` parameter is missing, the tool will not run and prompt you to provide the required device parameter.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

Happy coding!
