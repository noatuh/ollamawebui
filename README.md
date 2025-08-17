# Ollama Web UI

Ollama Web UI is a sleek and user-friendly web interface for interacting with Ollama. This project provides a simple yet powerful way to manage and visualize your Ollama data.

## Features

- **Intuitive Design**: A clean and modern interface for seamless user experience.
- **Customizable**: Easily adaptable to your specific needs.
- **Lightweight**: Minimal dependencies for quick setup and performance.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package manager)
- A modern web browser

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/noatuh/ollamawebui.git
   cd ollamawebui
   ```

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:

   ```bash
   python server.py
   ```

4. Open your browser and navigate to `http://localhost:5000`.

## File Structure

```plaintext
ollamawebui/
├── memories.txt          # Data storage file
├── README.md             # Project documentation
├── server.bat            # Windows batch file to start the server
├── server.py             # Python server script
├── static/               # Static assets (e.g., favicon, CSS, JS)
│   └── favicon.ico       # Favicon for the web app
├── templates/            # HTML templates
│   └── index.html        # Main HTML file
```

## Contributing

We welcome contributions! To get started:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push them to your fork.
4. Submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For questions or feedback, please reach out to [noatuh](https://github.com/noatuh).
