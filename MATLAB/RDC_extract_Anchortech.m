function [Data_time,Tsweep]= RDC_extract_Anchortech(fNameIn)
        fileID = fopen(fNameIn, 'r');
        dataArray = textscan(fileID, '%f');
        fclose(fileID);
        radarData = dataArray{1};
        clearvars fileID dataArray ans;
        fc = radarData(1); % Center frequency
        Tsweep = radarData(2); % Sweep time in ms
        Tsweep=Tsweep/1000; %then in sec
        NTS = radarData(3); % Number of time samples per sweep
        Bw = radarData(4); % FMCW Bandwidth. For FSK, it is frequency step;
        % For CW, it is 0.
        Data = radarData(5:end); % raw data in I+j*Q format
        
        fs=NTS/Tsweep; % sampling frequency ADC
        record_length=length(Data)/NTS*Tsweep; % length of recording in s
        nc=record_length/Tsweep; % number of chirps
        
        %% Reshape data into chirps and do range FFT (1st FFT)
        Data_time=reshape(Data, [NTS nc]);