Python: (3.6 - 3.8.5)

git clone https://github.com/rifkyadiii/airmouse.git)

conda create --name gest python=3.8.5

conda activate gest

pip install -r requirements.txt

conda install PyAudio

conda install pywin32

cd C:\Users\.....\airmouse\src

python Proton.py (Run Chatbot)

Uncomment 2 baris terakhir Gesture_Controller.py

python Gesture_Controller.py (Run Mouse Aja)


Bikin .exe:

pip install pyinstaller

pyinstaller --onefile --add-data "src\\web;src\\web" src\\Proton.py

