# Operation Profile Report Generator for Energy Dataset

[![Python Versions][pyversion-button]][md-pypi]

[md-pypi]: https://pypi.org/project/Markdown/
[pyversion-button]: https://img.shields.io/pypi/pyversions/Markdown.svg

Introduction
---
This guide is designed to help you generate operation profile reports for an Energy dataset provided Python script. The reports analyze equipment performance based on data provided and are visualized through charts and tables. The Python script reads the data from CSV files and generates the HTML reports in the `charts/` directory and viewable on your browser.

Prerequisites
---
- Python versions 3.8, 3.9, or 3.10 installed on your computer.
- Basic familiarity with command-line operations.
- Access to the CSV data files.

### NOTE
```
If you do not meet the minimum requirements, that's okay! 

You can still run the script on your local machine by skipping over to the section 'Runing The Executable File' within this guide.
```

Getting Started
---
#### Clone the Repository
First, clone this repository to your local machine using the command below:

```bash
git clone [repository-url]
# Replace [repository-url] with the actual URL of this repository.
```

Navigate to the Project Directory
Change the directory to where the repository is cloned.

```bash
cd path/to/repository
```

Please refer to the following links for more information on cloning a repository:
- [Clonning a repository from GitHub](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)
- [Clonning a repository from Bitbucket](https://support.atlassian.com/bitbucket-cloud/docs/clone-a-repository/)

---

#### Note
If this repository is being shared with you via a zip file or other means, you can skip cloning the repository steps. 

Please do the following below by setting up a virtual environment and installing the required packages using the requirements.txt file.:

Set Up a Virtual Environment
---
Before running the script, set up a Python virtual environment. This will ensure that the required packages do not conflict with other Python projects on your system.

For Windows:

```bash
python -m venv venv
venv\Scripts\activate
```
For macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install Dependencies
---
With the virtual environment activated, install the required Python packages using the requirements.txt file:

```
pip install -r requirements.txt
```

Usage
---
Before running the **main.py** script make sure to have the CSV data files in the **data/** directory. The CSV files should have the following column names:
```python
'Timestamp', 'Power (MW)', 'Press (psig)', 'Temp (°F)','PowerSwing (MW)'
```

### Run the Script

Run the script to generate the report by using a command-line interface (CLI) or an integrated development environment (IDE). The following command runs the script in the CLI:
    
```bash
python main.py
```

### Generated Reports

After running the script, check the `charts/` directory for the generated reports. The reports automatically open in your default web browser. The reports are saved as HTML files and contain charts and tables that analyze the equipment performance based on the provided data.

It is using a module called `plotly` to generate the charts and tables. You can take a screenshot of the charts and tables and save them as images to add to your reports. Every chart/table has a download button that allows you to save the chart/table as an image. This is located at the top right corner of the chart/table.

# Running The Executable File

If you do not have Python installed on your local machine, you can run the executable file  **main.exe**. The executable file is a standalone version of the main.py script that does not require Python to execute.

Make sure their are CSV data files in the **data/** directory that meet the requirements or else the Executable file will not run. Refer to `Usage` section of this guide for more information.

Refer to the main.log file to track the progress of the script.

Simply double-click the **main.exe** file to run the script and generate the reports.

_Note:_ Windows may display a security warning when running the executable file. Click `More info` and then `Run anyway` to proceed.

Refer to the `Directory and File Structure` section for more information about the directory structure and file contents.

### Generating Executable File

If you want to generate the executable file from the main.py script, you can use the `pyinstaller` package. First, install the `pyinstaller` package using the following command:

```bash 
pip install pyinstaller
``` 

Then, run the following command to generate the executable file:

```bash
pyinstaller --onefile main.py
```

Alternatively, if you are having issues with the above command, stating dependencies not found, you can use the following command:

```bash
# example of installing a dependency that is not found
pyinstaller --onefile --hidden-import=iapws --add-data "D:\PyScripts\energy_report_assessment\venv\Lib\site-packages\iapws;iapws" main.py
```


Troubleshooting
---
If you encounter any issues while installing packages or running the script, please ensure that:

- Your Python version is correct (3.8, 3.9, or 3.10).
- You have activated the virtual environment as described above.
- The CSV data files are placed in the correct directory (charts/).

For any further assistance, please contact the repository maintainer or your IT support.


Directory and File Structure
---
### charts/

The `charts/` directory contains the CSV data files used to generate the reports. The script reads the data from these files and generates the reports in the same directory.

### data/

The `data/` directory contains the CSV data files used to generate the reports. The script reads the data from these files and generates the reports in the same directory.

### venv/

The `venv/` directory contains the Python virtual environment used to install the required packages.

### deliverables.pdf

The `deliverables.pdf` file contains the deliverables of the project, including the project plan, report, and other relevant documents.

### main.log

The `main.log` file contains the log of the main script, providing information about its execution and any errors encountered.

### main.py

The `main.py` file is the main script that generates the operation profile reports.

### main.exe

The `main.exe` file is the executable version of the main script that generates the operation profile reports.

### README.md 

The `README.md` file is the project's main documentation, providing information about the project, its usage, and other relevant details.

### README.pdf 

The `README.pdf` file is the project's main documentation, providing information about the project, its usage, and other relevant details. The file is in PDF format rather than Markdown.

### requirements.txt

The `requirements.txt` file contains the required Python packages for the project.

### sandbox.ipynb

The `sandbox.ipynb` file is a testing and sandbox file used to assist in the development of the code.

Contributing
---
Your contributions are welcome! 

License
---
This project is licensed under the MIT License.

Authors
---

Jean Paul Mitterhofer  
[jp86mitter@gmail.com](https://innowatts.com)