# DeepSight: Image Retrieval System

### Overview
DeepSight is a web-based application designed to streamline image retrieval using natural language queries. It leverages the CLIP (Contrastive Language-Image Pre-training) model, to understand and associate images with text.

### Features
- Natural language image search using CLIP model
- Integration with Azure Blob Storage for image management
- User-friendly web interface for easy interaction
- Image pre-embedding for faster search results
- Lazy loading of images for improved performance
- Multi-image selection and download functionality
- Image enlargement feature for detailed viewing

### Prerequisites
- Python 3.7 or higher
- Azure Blob Storage account (for image storage)
- Git (for cloning the repository)

# Installation

## 1. Clone the repository:

Type: `git clone https://github.com/eirvav/TransoceanArtifactRetriever.git` in the terminal and navigate to the folder

## 2. Create a virtual environment:

### Creating Environments in Visual Studio Code

#### Using the Create Environment Command

To create local environments in Visual Studio Code using either Virtual Environments (`venv`) or Anaconda (`Conda`), you can follow these steps:

-  **Open the Command Palette**:
   
    Press `Ctrl+Shift+P` to open the Command Palette.

- **Search and Select the Command**:
   
   Type `Python: Create Environment` in the search bar and select the command.

- **Choose Environment Type**:
   
   A dropdown list will appear, allowing you to select `Venv`

- **Select Interpreter or Python Version**:
   
   When you choose `Venv`, a list of available Python interpreters will be displayed. Select one to use as the base for your virtual environment.
   
- **Environment Creation**:
   
   Once you've selected the desired interpreter or Python version, a notification will display the progress of the environment creation. The environment folder will be added to your workspace.

### Creating a Virtual Environment in the Terminal

If you prefer to create a virtual environment manually, use the following command in the terminal, where `.venv` is the name of the environment folder:

- On Windows:

    ```
    python -m venv .venv` or `py -3 -m venv .venv
    ```

- On macOS/Linux:
    > **Note**: You may need to install the `python3-venv` package first on Debian-based systems using `sudo apt-get install python3-venv`.

    ```
    python3 -m venv .venv
    ```


## 3. Activate the virtual environment:
- On Windows:
  ```
  .venv\Scripts\activate
  ```
- On macOS and Linux:
  ```
  source .venv/bin/activate
  ```

## 4. Install the required packages:

   ```
  pip install -r requirements.txt
  ```


# Usage 
### 1. Prepare `blob_retriever.py`
Write `az login` in the terminal, log in and select the approproate resource group.

Navigate to `blob_retriever.py` and fill in following information:

- Storage account name in the: `account_url`
- Container you want to use in: `container_name`
- Prefix to filter blobs by the directory structure in : `prefix`  


Run the `blob_retriever.py` file to download all the images. It should automatically create a folder in the correct directory

### 2. Start the embedding process
1. In the terminal, start the application with `python app.py`

2. You will get a prompt to type `y/n` to embed the images. Write `y` and hit enter. 

This process will take a few minutes.

3. After the embedding process is over, navigate over to `http://127.0.0.1:5000/` 

4. Enter a natural language query in the search box to find relevant images. 

5. Select images for download or click to enlarge them for a better view.

## Project Structure

- `app.py`: Main Flask application file
- `clip_image_retrieval.py`: CLIP model integration and image retrieval logic
- `blob_retriever.py`: Azure Blob Storage interaction
- `static/`: Directory for static files (CSS, JavaScript)
- `templates/`: HTML templates for the web interface

## Customization

- Modify the CLIP model or embedding process in `clip_image_retrieval.py`
- Adjust the UI by editing the HTML templates in the `templates/` directory and the CSS in `static/styles.css`
- Configure Azure Blob Storage settings in `blob_retriever.py`
