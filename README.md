Animal-vs-NonAnimal-Detection-YOLOv8

A desktop computer vision tool powered by a custom-trained YOLOv8 model that detects, classifies and counts animals versus non-animal objects in any image, with a simple point-and-click interface that requires no coding.

Application screenshot

Technologies Used
Python: Core logic, data preparation and application loop
YOLOv8 (Ultralytics): Object detection framework used for training and inference
PyTorch (CUDA): Deep learning backend, with GPU-accelerated training on an NVIDIA RTX graphics card
Tkinter + Pillow: Desktop graphical interface and on-image drawing
JupyterLab + Matplotlib: Step-by-step training notebook and visual testing
PyInstaller: Packaging the application into a standalone Windows .exe
Repository Structure
DetectorAnimaleFinal.py: The main application. It opens an interactive window where the user uploads any image from their computer and instantly receives the detection result.
YOLOv8_Animal_vs_NonAnimal.ipynb: The full training notebook. It downloads and prepares the dataset, trains the model and tests it on new images with automatic counting.
model_animal.pt: The final trained YOLOv8s model used by the application.
PornesteAplicatia.bat: One-click launcher for the application on Windows.
ConstruiesteAplicatia.bat: One-click script that builds the standalone .exe version of the application.
requirements.txt: Python libraries needed to run the project.
Features and Visual Output Configuration

The application works as a simple utility tool that anyone can use without touching any code:

Image Upload: The user presses Alege o poză (Choose a picture) and selects any image from their computer.
Instant Verdict: The app clearly answers whether the image contains animals (✅ DA / YES or ❌ NU / NO).
Automatic Counting: The number of detected animals and non-animal objects is displayed for every image.
Animals: Highlighted with green bounding boxes (dogs, cats, horses, birds, sheep, cows, elephants, bears, zebras, giraffes).
Non-Animal Objects: Highlighted with orange bounding boxes (people, phones, cups, remotes, cars, chairs, bicycles and other everyday objects).
Confidence Labels: Each box shows its class and how sure the model is (e.g. Animal 87%).
Save Result: The annotated image can be saved with one click (Salvează rezultatul).
Hardware Aware: The app automatically uses the NVIDIA GPU when available and falls back to the CPU otherwise.
How the Model Was Built
Dataset: Images and labels from COCO 2017, automatically converted from 80 categories into exactly two classes: 0: Non_Animal and 1: Animal.
Data Preparation: The notebook downloads only the images it needs, balances the classes and generates the data.yaml configuration file.
Training: The model was improved over several iterations, from a small YOLOv8n model trained on the CPU to a larger YOLOv8s model fine-tuned on the GPU with around 17,000 images.
Getting Started
Install the requirements (Python 3.12, Windows):
bash
   py -3.12 -m pip install -r requirements.txt
Double-click PornesteAplicatia.bat to open the application.
Optional: double-click ConstruiesteAplicatia.bat to build dist\DetectorAnimaleFinal\DetectorAnimaleFinal.exe, a standalone version that runs without Python.

To retrain the model, open YOLOv8_Animal_vs_NonAnimal.ipynb in JupyterLab and run the cells in order.

Credits
Ultralytics YOLOv8 (AGPL-3.0)
COCO Dataset (annotations under CC BY 4.0)
