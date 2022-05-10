function RDC = RDC_extract(fNameIn)
    fileID = fopen(fNameIn, 'r'); % open file
    Data = fread(fileID, 'int16');% DCA1000 should read in two's complement data
    fclose(fileID); % close file
    
    fileSize = size(Data, 1);
    numTX = 2;
    numRX = 4;
    NTS = 256; %64 Number of time samples per sweep
    numChirps = ceil(fileSize/2/NTS/numRX);
    
    LVDS = zeros(1, fileSize/2);
    LVDS(1:2:end) = Data(1:4:end) + sqrt(-1)*Data(3:4:end);
    LVDS(2:2:end) = Data(2:4:end) + sqrt(-1)*Data(4:4:end);
    % check array size (if any frames were dropped, pad zeros)
    if length(LVDS) ~= NTS*numRX*numChirps
       numpad =  NTS*numRX*numChirps - length(LVDS); % num of zeros to be padded
       LVDS = padarray(LVDS, [0 numpad],'post');
    end
    
    if rem(length(LVDS), NTS*numRX) ~= 0
          LVDS = [LVDS zeros(1, NTS*numRX - rem(length(LVDS), NTS*numRX))];  
    end
    LVDS = reshape(LVDS, NTS*numRX, numChirps);
    %% If BPM, i.e. numTX = 2, see MIMO Radar sec. 4.2
    
    if numTX == 2
            if rem(size(LVDS,2),2) ~= 0
                    LVDS = [LVDS LVDS(:,end)];
                    numChirps = numChirps + 1;
            end
            BPMidx = [1:2:numChirps-1];
            LVDS_TX0 = 1/2 * (LVDS(:,BPMidx)+LVDS(:,BPMidx+1));
            LVDS_TX1 = 1/2 * (LVDS(:,BPMidx)-LVDS(:,BPMidx+1));
            LVDS0 = kron(LVDS_TX0,ones(1,2));
            LVDS1 = kron(LVDS_TX1,ones(1,2));
            LVDS = zeros(NTS*numRX*numTX,numChirps);
            LVDS(1:end/2,:) = LVDS0;
            LVDS(end/2+1:end,:) = LVDS1;
    end
    %%
    Data = zeros(numChirps*NTS, numRX*numTX);
    for i = 1:numRX*numTX
        Data(:,i) = reshape(LVDS((i-1)*NTS+1:i*NTS,:),[],1);
    end
    
    RDC = reshape(Data,NTS,numChirps, numRX*numTX); 
    
end