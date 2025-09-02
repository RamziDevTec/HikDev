sudo apt update
sudo apt install -y wget build-essential libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libffi-dev libbz2-dev libjpeg-dev libpng-dev libtiff-dev libsm6 libxext6 libxrender-dev

# Python 3.10 herunterladen
wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz

# Entpacken
tar xvf Python-3.10.0.tgz
cd Python-3.10.0

# Kompilieren und installieren
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall

cd ..
rm Python-3.10.0.tgz