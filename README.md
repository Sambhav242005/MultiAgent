# AI Agent for Internship

This project is developed to provide an AI agent that aids in managing tasks during your internship.  

## Demo

https://github.com/Sambhav242005/MultiAgent/assets/demo.mp4

Or view the embedded video below:

![Demo Video](assets/demo.mp4)

## Features
- Intelligent task management.
- Automated reminders and notifications.
- Seamless integration with your workflow.
- Email and PDF processing agents.
- Memory management for persistent context.
- Sample input files for testing.

## Setup Instructions

### 1. Clone the repository
Clone this repository to your local machine using:
```sh
https://github.com/Sambhav242005/MultiAgent
cd MultiAgent
```

### 2. Create a virtual environment (optional but recommended)
```sh
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install the required dependencies
```sh
pip install -r requirement.txt
```

### 4. Generate sample files (optional)
Sample input files for emails, PDFs, and JSON are provided in the `sample_inputs/` directory. If you want to regenerate or create new sample files, run:
```sh
python gen_sample_files.py
```
This will create or update sample emails, PDFs, and JSON files in the `sample_inputs/` folder.

### 5. Run the main script
```sh
python main.py
```

## Usage
After running the main script, follow the on-screen instructions to interact with the AI agent. You can test the agent using the sample files in the `sample_inputs/` directory.

## Project Structure
- `main.py`: Entry point for the application.
- `agents/`: Contains different agent modules (e.g., emailAgent, pdfAgent).
- `memory/`: Handles persistent memory and database.
- `sample_inputs/`: Example files for testing (emails, PDFs, JSON).
- `gen_sample_files.py`: Script to generate sample input files.
- `requirement.txt`: List of Python dependencies.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request. For major changes, open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
