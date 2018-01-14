### Brain Powered python script
The `eeg.py` script allows users to visualize the powers of eeg signals using scatterplots. 

### Usage
The folders containing the signals can be selected using the `-f` or `--folder` commandline option (see Examples). The sample rate can be adjusted using the `-s` or `--sample_rate` commandline flag, it is 256 by default (see Examples). The frequency band is 8Hz to 13Hz by default but can be adjusted as well. Again, see the Example section for its usage. 

### Requirements
Besided python 3, these modules are required and can be installed using the command `pip3 install -r requirements.txt` when inside the project root folder.
* scipy
* matplotlib
* sklearn

### Data organization
We organized our eeg data in the following way. The root folder data is divided in multiple folders, each containing all the data about a particular individual. The folders of the individuals are divided into multiple folders each containing a single action, such as moving your hand or feet. Inside these action folders are two files, c1.mat and c2.mat. These are the channels of the actions and contain all records of that particular action. c1.mat and c2.mat are required to be present in the selected folders when using the eeg.py script. The data can be found on a private repository and is not available to the public.
```sh
data\
    personA
    personB
    personC\
        foot-right-cond
        hand-left-base
        hand-left-cond
        hand-right-cond\
            c1.mat
            c2.mat
```

### Examples
```sh
# Sample rate is 256 and band is 8 to 13 by default
./eeg.py --folder data/hand-left-cond data/foot-right-cond/
# Using a 3 different actions, a different sample rate and a different band
./eeg.py --folder data/hand-left-cond data/hand-right-cond data/foot-right-cond/ --sample_rate 512 --band 3 8
```

