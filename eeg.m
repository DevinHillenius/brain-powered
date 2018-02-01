// Get hardware info
daqinfo = daqhwinfo('gmlplusdaq');
comport = str2double(daqinfo.InstalledBoardIds{1});

// Create analoginput object with hardware
ai = analoginput('gmlplusdaq', comport);

// Set channels and length of recording
addchannel(ai, 1);
addchannel(ai, 2);
set(ai, 'SamplesPerTrigger', 256 * 3);

// Start recording and get the data
start(ai);
data = getdata(ai);
