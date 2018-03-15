function bp
    ai = init();
    filename = 'data.csv';
    i = 0;
    last_sample = 0
    out = daqmem
    
    while 1 > 0
        
        if ai.SamplesAcquired - last_sample > 260
            data = peekdata(ai, 256);
            csvwrite(filename, data);
            fclose('all');
            i = i + 1;
            strcat('Samples Acq: ',num2str(ai.SamplesAcquired))
            strcat('Sample nr: ', num2str(i))
            last_sample = ai.SamplesAcquired;
        end
    end 
    
    stop(ai);
end

function ai = init
    info = getDaqDevice('gmlplusdaq');
    ai = analoginput(info.AdaptorName, info.comport);

    addchannel(ai, 1);
    addchannel(ai, 2);
    set(ai,'SamplesPerTrigger', Inf);
    daqmem(ai, 640000);
    start(ai);
    
end

